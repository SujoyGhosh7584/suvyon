from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.auth import (
    AuthenticationError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register global exception handlers.
    """

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_already_exists_handler(
        request: Request,
        exc: EmailAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Email is already registered.",
            },
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid email or password.",
            },
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(
        request: Request,
        exc: InactiveUserError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "User account is inactive.",
            },
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authentication failed.",
            },
        )
