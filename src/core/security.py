import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JOSEError, jwt

from src.auth.exceptions import TokenInvalidError
from src.auth.models import Token, TokenPayload
from src.core.config import security_settings
from src.database.redis import is_jti_blacklisted

log = logging.getLogger(__name__)

password_context = PasswordHasher()


_serializer = URLSafeTimedSerializer(
    secret_key=security_settings.JWT_SECRET_KEY,
    salt="activate",
    signer_kwargs={"digest_method": hashlib.sha3_512},
)


def generate_token_urlsafe(
    data: dict,
    salt: str | None = "activate",
) -> str:
    return _serializer.dumps(data, salt)


def decode_token_urlsafe(
    token: str,
    expiry: timedelta | None,
    salt: str | None = "activate",
) -> dict[str, Any] | None:
    try:
        return _serializer.loads(
            token, max_age=expiry.total_seconds() if expiry else None, salt=salt
        )
    except (BadSignature, SignatureExpired):
        return None


def hash_password(password: str) -> str:
    """Hashes a plaintext password."""
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return password_context.verify(password_hash, plain_password)
    except VerifyMismatchError:
        return False


async def create_access_token(
    payload: dict,
    expiry: timedelta = timedelta(minutes=20),
) -> str:
    return jwt.encode(
        claims={
            **payload,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET_KEY,
    )


def decode_access_token(token: str) -> TokenPayload | None:
    try:
        return jwt.decode(
            token=token,
            key=security_settings.JWT_SECRET_KEY,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
    except JOSEError:
        return None


# Dependency to extract token from HttpOnly cookie
async def get_access_token_from_cookie(request: Request) -> str:
    """Extracts the access token from the HttpOnly cookie."""
    token = request.cookies.get("access_token")
    if not token:
        # Raise 401 Unauthorized if the cookie is missing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing access token cookie.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


async def verify_access_token(
    # Use the new cookie dependency
    token: Annotated[str, Depends(get_access_token_from_cookie)],
) -> TokenPayload:
    payload = decode_access_token(token)

    if payload is None or await is_jti_blacklisted(payload["jti"]):
        log.warning(f"Invalid or blacklisted token received: {token[:10]}...")
        raise TokenInvalidError()

    # Token must contain user information
    if "user" not in payload:
        log.error(f"Token missing 'user' claim: {payload}")
        raise TokenInvalidError(detail="Token payload is invalid.")

    return payload
