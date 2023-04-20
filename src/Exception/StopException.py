from src.Exception.AbstractException import AbstractException


class StopCreationException(AbstractException):
    pass


class StopException(AbstractException):
    pass


class StopNotFoundException(AbstractException):
    pass


class StopDeletedException(AbstractException):
    pass
