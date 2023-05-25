import datetime

from src.Exception.ErrorCodes import ErrorCodes
from src.Exception.LineException import *
from src.Exception.RouteException import *
from src.Route import Route
from src.util import Utils


class Schedule:
    counter = 0

    def __init__(self, map):
        Schedule.counter += 1
        self.id = Schedule.counter
        self.lines = {}
        self.routes = {}
        self.map = map

    def newroute(self, route: Route):
        for stop in route.stops:
            if not self.map.stops[stop]:
                return RouteStopIdNotFoundException(ErrorCodes.ByRoute.ROUTE_STOP_ID_NOT_FOUND,
                f"Given stop id with {stop} is not in the map\n")

        self.routes[route.id] = route
        return route

    def getroute(self, routeId):
        route = self.routes[routeId]
        if not route:
            raise RouteNotFoundException(ErrorCodes.ByRoute.ROUTE_NOT_FOUND, f"Route with id {route.id} cannot found")
        return route

    def updateroute(self, routeId, stopIds):
        route = self.getroute(routeId)
        route.stops = stopIds
        self.routes[routeId] = route
        return route

    def delroute(self, routeId):
        self.routes[routeId] = None

    def listroutes(self):
        result = {}
        for routeId, route in self.routes.items():
            result[routeId] = route.get()
        return result

    def addLine(self, line):
        self.lines[line.id] = line

    def getLine(self, line_id):
        if not self.lines[line_id]:
            raise LineNotFoundException(ErrorCodes.ByLine.LINE_NOT_FOUND, f"Line with id {line_id} cannot found")
        return self.lines[line_id]

    def updateLine(self, line_id, start: datetime.time, end: datetime.time, rep: datetime.time, route: Route,
                   description=""):
        line = self.getLine(line_id)
        line.start_time = start
        line.end_time = end
        line.rep = rep
        line.route = route
        line.description = description
        return line

    def delLine(self, line_id):
        self.lines[line_id] = None

    def listlines(self):
        result = {}
        for lineId, line in self.routes:
            result[lineId] = line.get()
        return result

    def lineinfo(self, lineId):
        return self.lines[lineId].get()

    def calculateEstimatedTimes(self, lineId, expectedStopId):
        line = self.lines[lineId]
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

    # may change according to the data flow
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
