class ErrorCodes:
    class ByRoute:
        ROUTE = 1000
        ROUTE_DELETED = 1001
        ROUTE_NOT_FOUND = 1002
        ROUTE_ALREADY_DELETED = 1003
        ROUTE_STOP_ID_NOT_FOUND = 1004

    class ByStop:
        STOP_NOT_FOUND = 1100

    class ByLine:
        LINE_NOT_FOUND = 1200
        LINE_DELETED = 1201
