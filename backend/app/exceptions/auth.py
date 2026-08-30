class AuthenticationError(Exception):
    """
    Base exception for authentication errors.
    """

    pass


class InvalidCredentialsError(AuthenticationError):
    """
    Raised when user credentials are invalid.
    """

    pass


class EmailAlreadyExistsError(AuthenticationError):
    """
    Raised when attempting to register an existing email.
    """

    pass


class InactiveUserError(AuthenticationError):
    """
    Raised when an inactive user attempts to authenticate.
    """

    pass


class OtpError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OtpInvalidError(OtpError):
    def __init__(self, message: str = "Invalid or expired code.") -> None:
        super().__init__(message)


class OtpRateLimitedError(OtpError):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            f"Please wait {retry_after_seconds} seconds before requesting another code."
        )
