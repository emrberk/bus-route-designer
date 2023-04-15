import datetime
import uuid

from src.Route import Route


class Line:
    counter = 0

    def __init__(self, start: datetime.time, end: datetime.time, rep: datetime.time, route: Route, description=""):
        Line.counter += 1
        self.id = Line.counter
        self.__external_id = uuid.uuid4()
        self.description = description
        self.start_time = start
        self.end_time = end
        self.rep = rep
        self.route = route
        self.active = True

    def __str__(self):
        return f"Line {self.id}: starts at = {self.start_time}, ends at = {self.end_time}," \
               f" route id = {self.route.id}, description = {self.description}, active = {self.active}"

    def getExternalId(self):
        return self.__external_id
