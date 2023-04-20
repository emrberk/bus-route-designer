import uuid


class Route:
    counter = 0

    def __init__(self, stopids):
        Route.counter += 1
        self.id = Route.counter
        self.__external_id = uuid.uuid4()
        self.stops = stopids
        self.active = True

    def __str__(self):
        return f"Route {self.id}: stops={self.stops}, active={self.active}"

    def getStop(self, index):
        return self.stops[index]
