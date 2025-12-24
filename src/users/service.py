import logging
from datetime import timedelta
from uuid import UUID

from fastapi_mail import MessageType
from pydantic import EmailStr
from sqlmodel import select

from src.auth.exceptions import EmailVerificationError
from src.core.config import app_settings
from src.core.security import (
    decode_token_urlsafe,
    generate_token_urlsafe,
    hash_password,
    verify_password,
)
from src.database.db import DBSession
from src.entities.user import User
from src.users.exceptions import (
    InvalidEmailError,
    PasswordMismatchError,
    UnauthorizedUserError,
    UserNotFoundError,
    UserUpdateError,
)
from src.users.models import PasswordChange
from src.worker.tasks import send_mail, send_mail_template


class UserService:
    def __init__(self, session: DBSession):
        self.session = session

    async def _get_user_by_email(self, email: EmailStr) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def verify_user_email(self, token: str):
        data = decode_token_urlsafe(
            token,
            expiry=timedelta(minutes=5),
            salt="activate",
        )
        if data is None or "user_id" not in data:
            raise EmailVerificationError(detail="Invalid or expired token.")

        user = await self.session.get(User, UUID(data["user_id"]))
        if not user:
            raise EmailVerificationError(detail="User not found.")

        user.email_verified = True
        await self.session.commit()

    async def password_reset_link(self, email: EmailStr) -> None:
        """
        Generate and send password reset token via email.
        Args:
            email: User's email address
        Raises:
            UserNotFoundError: If user with email doesn't exist
        """
        user = await self._get_user_by_email(email)
        if user is None:
            # Don't reveal if email exists (security best practice)
            logging.info(f"Password reset requested for non-existent email: {email}")
            raise UserNotFoundError()
        # Generate secure token (expiry validated on decode)
        token = generate_token_urlsafe(
            {"user_id": str(user.id)},
            salt="upgrade",
        )
        # reset_url = f"http://{app_settings.APP_DOMAIN}/reset-password?token={token}"
        reset_url = f"http://localhost:8000/reset-password?token={token}"

        # Send reset email asynchronously
        send_mail.delay(
            recipients=[user.email],
            subject="FastTodo Account Password Reset",
            body=f"Click here to reset your password: {reset_url}\n\nThis link expires in 5 minutes.",
            subtype=MessageType.plain.value,
        )

        logging.info(f"Password reset email sent to user: {user.id}")

    async def reset_password(self, token: str, new_password: str) -> dict:
        """
        Reset user password with valid token.

        Args:
            token: Password reset token from email
            new_password: New password (must be 8+ chars)

        Returns:
            Dictionary with success message

        Raises:
            EmailVerificationError: If token is invalid or expired
            UserNotFoundError: If user not found
            ValueError: If password is too weak
        """
        # Validate password strength
        if not new_password or len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Decode and validate token
        data = decode_token_urlsafe(
            token=token,
            expiry=timedelta(minutes=5),
            salt="upgrade",
        )

        if data is None or "user_id" not in data:
            logging.warning("Invalid or expired password reset token attempted")
            raise EmailVerificationError(detail="Invalid or expired reset link")

        # Get user and update password
        try:
            user = await self.session.get(User, UUID(data["user_id"]))
            if not user:
                raise UserNotFoundError()

            # Hash and update password
            user.password_hash = hash_password(new_password)
            await self.session.commit()

            logging.info(f"Password successfully reset for user: {user.id}")

            return {
                "detail": "Password has been reset successfully. Please log in with your new password."
            }

        except Exception as e:
            await self.session.rollback()
            logging.error(f"Error resetting password: {str(e)}")
            raise

    async def change_password(
        self, email: EmailStr, password_change: PasswordChange
    ) -> None:
        user = await self._get_user_by_email(email)
        # Verify current password
        if not verify_password(
            password_change.current_password,
            user.password_hash,
        ):
            raise PasswordMismatchError()

        # Verify new passwords match
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(
                f"Password mismatch during change attempt for user ID: {email}"
            )
            raise PasswordMismatchError()

        # Update password
        user.password_hash = hash_password(password_change.new_password)

        await self.session.commit()
        send_mail.delay(
            recipients=[user.email],
            subject="Password Change",
            body=f"Hello {user.username}, your password has been changed successfully. If you did not perform this action, please contact support immediately.",
            subtype=MessageType.plain.value,
        )

        return {"detail": "Successfully changed password"}
