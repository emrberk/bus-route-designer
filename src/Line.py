import datetime
import uuid
import json
from src.Route import Route


class Line:
    counter = 0

    def __init__(self, start: datetime.time, end: datetime.time, interval: datetime.timedelta, route: Route, description=""):
        Line.counter += 1
        self.id = Line.counter
        self.__external_id = uuid.uuid4()
        self.description = description
        self.start_time = start
        self.end_time = end
        self.interval = interval
        self.route = route

    def get(self):
        return {
            'id': self.id,
            'description': self.description,
            'start_time': self.start_time.strftime("%H:%M:%S"),
            'end_time': self.end_time.strftime("%H:%M:%S"),
            'interval': str(self.interval),
            'route': self.route.get()
        }

    def createDailySimulationData(self, map):
        simulationData = {}
        departureTime = self.start_time
        busId = 0
        # For all buses that departure before the end time
        while departureTime < self.end_time:
            currentTime = departureTime
            # Create all simulation data inside this loop for a single bus
            for i in range(0, len(self.route.stops) - 1):
                simulationData[currentTime.strftime("%H:%M:%S")] = {
                    "line": self.id,
                    "type": "departure",
                    "stop": str(self.route.stops[i]),
                    "bus": busId,
                    "time": currentTime.strftime("%H:%M:%S")
                }
                # km, h
                distance, time = map.stopdistance(self.route.stops[i], self.route.stops[i + 1])
                timeInMinutes = datetime.timedelta(minutes=time * 60)
                currentTime = (datetime.datetime.combine(datetime.datetime.min, currentTime) + timeInMinutes).time()
                simulationData[currentTime.strftime("%H:%M:%S")] = {
                    "line": self.id,
                    "type": "arrival",
                    "stop": str(self.route.stops[i + 1]),
                    "bus": busId,
                    "time": currentTime.strftime("%H:%M:%S")
                }
                waitTime = datetime.timedelta(minutes=0.5)
                currentTime = (datetime.datetime.combine(datetime.datetime.min, currentTime) + waitTime).time()
            busId += 1
            departureTime = (datetime.datetime.combine(datetime.datetime.min, departureTime) + self.interval).time()
        return simulationData

    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

    def getExternalId(self):
        return self.__external_id
