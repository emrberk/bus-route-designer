import uuid
import json


class Route:
    counter = 0

    def __init__(self, stopids):
        Route.counter += 1
        self.id = Route.counter
        self.__external_id = uuid.uuid4()
        self.stops = stopids

    def get(self):
        return {
            'id': self.id,
            'stops': [stop.get() for stop in self.stops]
        }

    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

    def getStop(self, index):
        return self.stops[index]
