from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm


from src.auth.models import UserCreate
from src.core.dependencies import AuthServiceDep, UserServiceDep
from src.core.security import (
    decode_access_token,
    get_access_token_from_cookie,
)
from src.database.redis import add_jti_to_blacklist
from src.rate_limiting import limiter
from src.tags import APITags
from src.users.models import UserResponse

router = APIRouter(prefix="/auth", tags=[APITags.AUTH])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "The user has been created successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request.",
        },
    },
)
@limiter.limit("5/minute")
async def register(
    credentials: UserCreate,
    service: AuthServiceDep,
    user: UserServiceDep,
    request: Request,
) -> UserResponse:
    return await service._register(credentials, user_service=user)


@router.post("/token")
@limiter.limit("5/minute")
async def login(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
    user: UserServiceDep,
    response: Response,
    request: Request,
):
    token = await service._login(
        request_form.username, request_form.password, user_service=user
    )

    # Set the HttpOnly, Secure cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Prevents client-side JS access (XSS defense)
        secure=False,  # Allow HTTP for development (set to True in production)
        max_age=service.access_token_expiry,  # Use expiry time from service
        samesite="Lax",  # Recommended setting for CSRF mitigation
    )

    # Return a success message, NOT the token in the body
    return {"detail": "Login successful"}


@router.get("/verify", include_in_schema=False)
async def verify_user_email(token: str, user_service: UserServiceDep, request: Request):
    await user_service.verify_user_email(token)
    return {"Details": "Your account is verified successfully"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    access_token: Annotated[str | None, Depends(get_access_token_from_cookie)] = None,
):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Allow HTTP for development
        samesite="Lax",
    )

    # 2. Add JWT to blacklist for immediate invalidation
    if access_token:
        # Decode the token to get the JTI (JWT ID) for blacklisting
        payload = decode_access_token(access_token)
        # if payload and payload["jti"]:
        if payload and getattr(payload, "jti", None):
            await add_jti_to_blacklist(payload["jti"])

    # Return 204 No Content
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
