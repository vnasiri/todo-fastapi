import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from fastapi_mail import MessageType

from src.auth.exceptions import (
    EmailVerificationError,
    InvalidCredentialsError,
    PasswordTooWeakError,
    UserAlreadyExistsError,
)
from src.auth.models import UserCreate
from src.core import security
from src.core.config import app_settings
from src.database.db import DBSession
from src.entities.user import User
from src.users import models
from src.worker.tasks import send_mail

if TYPE_CHECKING:
    from src.core.dependencies import UserServiceDep


class AuthService:
    # 🚨 FIX: Define an explicit expiry time for the access token
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

    def __init__(self, session: DBSession):
        self.session = session

    @property
    def access_token_expiry(self) -> int:
        # Return in seconds for max_age
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    async def _register(
        self, credentials: UserCreate, user_service: UserServiceDep
    ) -> models.UserResponse:
        existing_user = await user_service._get_user_by_email(credentials.email)

        # If user exists but not verified, just return their existing account
        if existing_user and not existing_user.email_verified:
            # Send verification email again
            await self._send_verification_email(existing_user)
            return models.UserResponse.model_validate(existing_user)

        # If user exists with verified email, they can't register again
        if existing_user and existing_user.email_verified:
            raise UserAlreadyExistsError(
                detail=f"User with email {credentials.email} already exists.",
            )

        if not self.is_strong(credentials.password):
            raise PasswordTooWeakError()

        user = User(
            **credentials.model_dump(exclude=["password"]),
            password_hash=security.hash_password(credentials.password),
            email_verified=False,  # Require email verification
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        # Send verification email
        await self._send_verification_email(user)

        return models.UserResponse.model_validate(user)

    async def _send_verification_email(self, user: User) -> None:
        """Send email verification link to user"""
        token = security.generate_token_urlsafe(data={"user_id": str(user.id)})
        verify_link = f"http://localhost:8000/verify-email?token={token}"

        send_mail.delay(
            recipients=[user.email],
            subject="Verify Your Email - Todos App",
            body=f"Click here to verify your email: {verify_link}",
            subtype=MessageType.plain.value,
        )

    async def _authenticate_user(
        self, email: str, password: str, user_service: UserServiceDep
    ):
        user = await user_service._get_user_by_email(email)

        if not user or not security.verify_password(password, user.password_hash):
            print(user)
            logging.warning(f"Failed authentication attempt for email: {email}")
            raise InvalidCredentialsError()

        # Check if the hash needs an upgrade (re-hashing)
        if security.password_context.check_needs_rehash(user.password_hash):
            new_hash = security.password_context.hash(password)
            user.password_hash = new_hash
            await self.session.commit()

        return user

    async def _login(
        self, email: str, password: str, user_service: UserServiceDep
    ) -> str:
        user: User = await self._authenticate_user(email, password, user_service)

        token = await security.create_access_token(
            payload={
                "user": {
                    "sub": user.email,
                    "user_id": str(user.id),
                },
            },
            expiry=timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return token

    def is_strong(self, password: str) -> bool:
        return len(password) >= 8
