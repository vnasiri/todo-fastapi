from typing import Optional

from fastapi import status

from src.exceptions import DomainError


class UserError(DomainError):
    """Base class for all user-related errors."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = "User-related operation failed."

    def __init__(
        self, *, status_code: Optional[int] = None, detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status_code or self.status_code,
            detail=detail or self.default_detail,
        )


class UserNotFoundError(UserError):
    """Raised when a user is not found."""

    def __init__(self, *, user_id: Optional[int] = None, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or f"User with ID {user_id} not found.",
        )


class UnauthorizedUserError(UserError):
    """Raised when a user is not authorized to perform an action."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or "User is not authorized to perform this action.",
        )


class UserUpdateError(UserError):
    """Raised when a user update fails (e.g., invalid data)."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Failed to update user information.",
        )


class InvalidEmailError(UserError):
    """Raised when an invalid email address is provided during update or registration."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "The provided email address is invalid.",
        )


class PasswordMismatchError(UserError):
    """Raised when the old and new passwords do not match during an update."""

    def __init__(self, *, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "The old password does not match the provided one.",
        )
