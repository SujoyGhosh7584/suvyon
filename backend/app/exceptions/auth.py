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
