from src.Exception.AbstractException import AbstractException


class LineCreationException(AbstractException):
    pass


class LineException(AbstractException):
    pass


class LineNotFoundException(AbstractException):
    pass


class LineDeletedException(AbstractException):
    pass
