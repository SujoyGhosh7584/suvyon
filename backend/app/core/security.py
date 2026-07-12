from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ------------------------------------------------------------------
# Password Hashing
# ------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against its hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ------------------------------------------------------------------
# JWT Tokens
# ------------------------------------------------------------------


def _create_token(
    subject: str,
    expires_delta: timedelta,
) -> str:
    """
    Create a signed JWT.
    """

    expire = datetime.now(timezone.utc) + expires_delta

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(subject: str) -> str:
    """
    Create an access token.
    """
    return _create_token(
        subject,
        timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )


def create_refresh_token(subject: str) -> str:
    """
    Create a refresh token.
    """
    return _create_token(
        subject,
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        ),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.
    Raises JWTError if invalid.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
