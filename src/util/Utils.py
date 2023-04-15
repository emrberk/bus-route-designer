import math
import sys
import numpy as np
import datetime


from src.Point import Point


def euclideanDistance(p1: Point, p2: Point) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def dot(p0: Point, p1: Point) -> float:
    return float(np.dot(tuple(p0), tuple(p1)))


def calculateD(p0: Point, p1: Point, p2: Point) -> float:
    return dot(p0 - p1, p2 - p1) / dot(p2 - p1, p2 - p1)


def calculateS(p1: Point, p2: Point, d: float) -> Point:
    return p1 + (p2 - p1) * d


def calculateDistance(p1: Point, p2: Point, location: Point) -> list:
    d = calculateD(location, p1, p2)
    point = (-1, -1)
    if d <= 0:
        point = p1
    elif d >= 1:
        point = p2
    else:
        point = calculateS(p1, p2, d)

    distance = euclideanDistance(location, point)
    return [point, distance]


def add_times(time1, time2):
    t1 = datetime.datetime.strptime(str(time1), '%H:%M:%S')
    t2 = datetime.datetime.strptime(str(time2), '%H:%M:%S')
    total = t1 + (t2 - datetime.datetime(1900, 1, 1))
    return datetime.time(total.hour, total.minute, total.second)


def time_difference(start, end):
    if end < start:
        end += datetime.timedelta(days=1)
    diff = datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(),
                                                                                             start)
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return datetime.time(hours, minutes, seconds)


def getTimeStr(time):
    return time.strftime("%H:%M")
