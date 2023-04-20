import datetime

from src.Exception.ErrorCodes import ErrorCodes
from src.Exception.LineException import *
from src.Exception.RouteException import *
from src.Route import Route
from src.util import Utils


class Schedule:
    def __init__(self, map):
        self.lines = []
        self.routes = []
        self.map = map

    def newroute(self, routes: list):
        for route in routes:
            for stop in route.stops:
                if stop not in self.map.stops:
                    raise RouteStopIdNotFoundException(ErrorCodes.ByRoute.ROUTE_STOP_ID_NOT_FOUND,
                                                       f"Given stop id with {stop} is not in the map")

        for route in routes:
            self.routes.append(route)
            return route

    def getroute(self, id):
        if not self.routes[id - 1].active:
            raise RouteDeletedException(message="This route is deleted by an Admin",
                                        error_code=ErrorCodes.ByRoute.ROUTE_DELETED)
        if not self.routes[id - 1]:
            raise RouteNotFoundException(ErrorCodes.ByRoute.ROUTE_NOT_FOUND, f"Route with id {id} cannot found")
        return self.routes[id - 1]

    def updateroute(self, id, stopIds):
        if not self.routes[id - 1].active:
            raise RouteDeletedException(message="This route is deleted by an Admin",
                                        error_code=ErrorCodes.ByRoute.ROUTE_DELETED)
        route = self.getroute(id - 1)
        route.stops = stopIds

    def delroute(self, id):
        if self.routes[id - 1] and self.routes[id - 1].active != False:
            self.routes[id - 1].active = False
        else:
            raise RouteDeletedException(ErrorCodes.ByRoute.ROUTE_ALREADY_DELETED, "This route is already deleted")

    def addLine(self, line):
        self.lines.append(line)

    def getLine(self, line_id):
        if not self.lines[line_id - 1].active:
            raise LineDeletedException(message="This line is deleted by an Admin",
                                       error_code=ErrorCodes.ByLine.LINE_DELETED)
        if not self.lines[line_id - 1]:
            raise LineNotFoundException(ErrorCodes.ByLine.LINE_NOT_FOUND, f"Line with id {line_id} cannot found")
        return self.lines[line_id - 1]

    def updateLine(self, line_id, start: datetime.time, end: datetime.time, rep: datetime.time, route: Route,
                   description=""):
        if not self.lines[line_id - 1].active:
            raise LineDeletedException(message="This line is deleted by an Admin",
                                       error_code=ErrorCodes.ByLine.LINE_DELETED)
        line = self.getLine(line_id)
        line.start_time = start
        line.end_time = end
        line.rep = rep
        line.route = route
        line.description = description

    def delLine(self, line_id):
        if self.lines[line_id - 1] and self.lines[line_id - 1].active != False:
            self.lines[line_id - 1].active = False
        else:
            raise LineDeletedException(ErrorCodes.ByLine.LINE_DELETED, "This line is already deleted")

    def lineinfo(self, id):
        print(self.lines[id - 1])
        return self.lines[id - 1]

    def calculateEstimatedTimes(self, lineId, expectedStopId):
        line = self.lines[lineId - 1]
        expectedIndex = line.route.stops.index(expectedStopId)
        start = line.start_time
        end = line.end_time
        times = []
        extra_times = [0] * len(line.route.stops)
        for stopId in line.route.stops:
            index = line.route.stops.index(stopId)
            stop = self.map.getStop(stopId)
            if index - 1 >= 0:
                extra_times[index] += extra_times[index - 1]
            if index + 1 != len(line.route.stops):
                nextStop = self.map.getStop(line.route.stops[index + 1])
                extra_time = self.map.stopdistance(stop.id, nextStop.id)[1]
                extra_times[index + 1] += extra_time
        while Utils.time_difference(start, end) > datetime.time(minute=0):
            time = Utils.add_times(start, line.rep)
            if extra_times[expectedIndex]:
                time = Utils.add_times(time, Utils.minToTime(extra_times[expectedIndex]))
            times.append(time)
            start = Utils.add_times(start, line.rep)
        return times

    def printLineReport(self, lines, stopId):
        for line in lines:
            print(f"Line {line} is passing from this stop")
            times = self.calculateEstimatedTimes(line, stopId)
            print(f"Estimated times :")
            for time in times:
                print(f"at {time}")

    def stopinfo(self, id):
        included_lines = []
        for line in self.lines:
            for stop in line.route.stops:
                index = 0
                if id == stop:
                    included_lines.append(line.id)
                index += 1

        print(f"STOP INFO {id}:\n Passed lines:")
        self.printLineReport(included_lines, id)
