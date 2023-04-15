import datetime
from src.util import Utils
import logging
from Route import Route


class Schedule:
    def __init__(self, map):
        self.lines = []
        self.routes = []
        self.map = map

    def newroute(self, routes: list):
        for route in routes:
            for stop in route.stops:
                if stop not in self.map.stops:
                    logging.error(f"Given stop id with {stop} is not in the map")
                    exit(500)

        for route in routes:
            self.routes.append(route)

    def getroute(self, id):
        if not self.routes[id - 1].active:
            logging.error("This route is deleted by an Admin")
            return
        return self.routes[id - 1]

    def updateroute(self, id, stopIds):
        if not self.routes[id - 1].active:
            logging.error("Deleted routes cannot be updated")
            return
        route = self.getroute(id - 1)
        route.stops = stopIds

    def delroute(self, id):
        self.routes[id - 1].active = False

    def getStopDescr(self, route, index):
        return self.map.getStop(route.getStop(index))

    def addLine(self, line):
        self.lines.append(line)

    def getLine(self, line_id):
        return self.lines[line_id - 1]

    def updateLine(self, line_id, start: datetime.time, end: datetime.time, rep: datetime.time, route: Route,
                   description=""):
        line = self.getLine(line_id)
        line.start_time = start
        line.end_time = end
        line.rep = rep
        line.route = route
        line.description = description

    def delLine(self, line_id):
        self.getLine(line_id - 1).active = False

    def lineinfo(self, id):
        print(self.lines[id - 1])
        return self.lines[id - 1]

    def calculateEstimatedTimes(self, lineId):
        line = self.lines[lineId - 1]
        start = line.start_time
        end = line.end_time
        times = []
        while Utils.time_difference(start, end) > datetime.time(minute=0):
            times.append(Utils.getTimeStr(Utils.add_times(start, line.rep)))
            start = Utils.add_times(start, line.rep)
        return times

    def printLineReport(self, lines):
        for line in lines:
            print(f"Line {line} is passing from this stop")
            times = self.calculateEstimatedTimes(line)
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
        self.printLineReport(included_lines)
