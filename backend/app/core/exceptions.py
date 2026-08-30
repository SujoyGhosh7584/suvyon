from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.auth import (
    AuthenticationError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    OtpInvalidError,
    OtpRateLimitedError,
)
from app.tools.email_tool import SmtpNotConfiguredError, SmtpSendError


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

    @app.exception_handler(OtpInvalidError)
    async def otp_invalid_handler(
        request: Request,
        exc: OtpInvalidError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(OtpRateLimitedError)
    async def otp_rate_limited_handler(
        request: Request,
        exc: OtpRateLimitedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": exc.message},
            headers={"Retry-After": str(exc.retry_after_seconds)},
        )

    @app.exception_handler(SmtpNotConfiguredError)
    async def smtp_not_configured_handler(
        request: Request,
        exc: SmtpNotConfiguredError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SmtpSendError)
    async def smtp_send_error_handler(
        request: Request,
        exc: SmtpSendError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )
