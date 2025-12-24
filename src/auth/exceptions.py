from typing import Optional

from fastapi import status

from src.exceptions import DomainError


class AuthError(DomainError):
    """Base class for all authentication-related errors."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
    default_detail: str = "Authentication failed."

    def __init__(
        self, *, status_code: Optional[int] = None, detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status_code or self.status_code,
            detail=detail or self.default_detail,
        )


class InvalidCredentialsError(AuthError):
    """Raised when the credentials (email/password) are invalid."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Invalid email or password.",
        )


class UserAlreadyExistsError(AuthError):
    """Raised when attempting to register an existing user."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "User already exists.",
        )


class TokenExpiredError(AuthError):
    """Raised when an authentication token has expired."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or "Token has expired.",
        )


class TokenInvalidError(AuthError):
    """Raised when an authentication token is invalid."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail or "Invalid token."
        )


class PasswordTooWeakError(AuthError):
    """Raised when the provided password is too weak during registration."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Password is too weak.",
        )


class EmailVerificationError(AuthError):
    """Raised when email is not verified."""

    def __init__(self, *, status_code=None, detail=None):
        super().__init__(
            status_code=status_code, detail=detail or "Email is not verified."
        )
