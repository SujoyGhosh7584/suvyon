from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(
    user_id: UUID,
) -> str:
    """
    Create a signed JWT access token.
    """

    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:
    """
    Decode and validate a JWT access token.

    Raises:
        InvalidTokenError:
            If the token is invalid or expired.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
    )


def get_user_id_from_token(
    token: str,
) -> UUID:
    """
    Extract the user ID from a JWT access token.
    """

    payload = decode_access_token(token)

    subject = payload.get("sub")

    if subject is None:
        raise InvalidTokenError(
            "Token subject is missing.",
        )

    return UUID(subject)
