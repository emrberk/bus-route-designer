import datetime
import uuid
import json
from src.Route import Route


class Line:
    counter = 0

    def __init__(self, start: datetime.time, end: datetime.time, interval: datetime.time, route: Route, description=""):
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
            'start_time': self.start_time.strftime("%H:%M"),
            'end_time': self.end_time.strftime("%H:%M"),
            'interval': self.interval.strftime("%M"),
            'route': self.route.get()
        }

    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

    def getExternalId(self):
        return self.__external_id
