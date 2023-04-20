from src.Exception.AbstractException import AbstractException


class RouteCreationException(AbstractException):
    pass


class RouteException(AbstractException):
    pass


class RouteNotFoundException(AbstractException):
    pass


class RouteStopIdNotFoundException(AbstractException):
    pass


class RouteDeletedException(AbstractException):
    pass
