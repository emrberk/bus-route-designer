from src.Exception.AbstractException import AbstractException


class UserCreationException(AbstractException):
    pass


class UserNotFoundException(AbstractException):
    pass


class PasswordException(AbstractException):
    pass
