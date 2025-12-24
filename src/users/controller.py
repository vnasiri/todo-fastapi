from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from pydantic import EmailStr

from src.auth.exceptions import EmailVerificationError
from src.core.dependencies import UserDep, UserServiceDep
from src.tags import APITags
from src.users.exceptions import UserNotFoundError
from src.users.models import PasswordChange, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=[APITags.USERS])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_dep: UserDep, service: UserServiceDep):
    """Get current authenticated user profile"""
    user = await service._get_user_by_email(user_dep.email)
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_dep: UserDep,
    update_data: UserUpdate,
    service: UserServiceDep,
    request: Request,
):
    """Update current user profile"""
    # Implementation would update user in database
    user = await service._get_user_by_email(user_dep.email)
    return UserResponse.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_dep: UserDep,
    password_change: PasswordChange,
    service: UserServiceDep,
    request: Request,
):
    """Change user password"""
    result = await service.change_password(user_dep.email, password_change)
    return result


@router.get("/forgot-password")
async def forgot_password(email: EmailStr, service: UserServiceDep):
    await service.password_reset_link(email)
    return {"detail": "Check email for password reset link."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    token: Annotated[str, Query()],
    password: Annotated[str, Form()],
    service: UserServiceDep,
    request: Request,
) -> dict:
    """
    Reset user password with valid token.

    Query Parameters:
        token: Password reset token from email (expires in 5 minutes)
    Form Parameters:
        password: New password (must be at least 12 characters)
    Returns:
        Success message with 200 status code
    Raises:
        HTTPException: 400 if token is invalid/expired or password is weak
        HTTPException: 404 if user not found
    """
    # Validate token is provided
    if not token or not token.strip():
        raise HTTPException(status_code=400, detail="Reset token is required")

    # Validate password is provided and meets minimum requirements
    if not password or len(password) < 12:
        raise HTTPException(
            status_code=400, detail="Password must be at least 12 characters long"
        )

    try:
        result = await service.reset_password(token, password)
        return result

    except EmailVerificationError as e:
        raise HTTPException(
            status_code=400, detail=e.detail or "Invalid or expired password reset link"
        )
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while resetting your password"
        )


@router.get("/dashboard")
async def dashboard(
    user_dep: UserDep,
    service: UserServiceDep,
    request: Request,
):
    user = await service._get_user_by_email(user_dep.email)
    return user.model_dump(exclude=["password_hash"])
