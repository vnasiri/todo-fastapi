from typing import Optional

from fastapi import HTTPException, status


class ApiException(HTTPException):
    """Base class for all custom API errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = "An unexpected error occurred."

    def __init__(self, *, status_code, detail: Optional[str] = None):
        self.status_code = status_code or self.status_code
        self.detail = detail or self.default_detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class DomainError(ApiException):
    """Base domain-level error for core business entities."""

    entity: str = "Entity"

    def __init__(
        self,
        *,
        status_code: Optional[int] = None,
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail or f"{self.entity} operation faild.",
        )
