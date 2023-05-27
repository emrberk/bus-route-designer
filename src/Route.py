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
            'stops': [str(stop) for stop in self.stops]
        }

    def getRouteCost(self, map):
        routeCost = {'time': 0, 'distance': 0}
        for i in range(0, len(self.stops) - 1):
            distance, time = map.stopdistance(self.stops[i], self.stops[i + 1])
            routeCost['time'] += time
            routeCost['distance'] += distance
        return routeCost


    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

    def getStop(self, index):
        return self.stops[index]
