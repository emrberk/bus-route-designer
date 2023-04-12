import math
import numpy as np


def euclideanDistance(p1: dict, p2: dict) -> float:
    return math.sqrt((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2)


def calculateD(p0: dict, p1: dict, p2: dict) -> float:
    p0T = (p0['x'], p0['y'])
    p1T = (p1['x'], p1['y'])
    p2T = (p2['x'], p2['y'])
    return np.dot(np.subtract(p0T, p1T), np.subtract(p2T, p1T)) / np.dot(np.subtract(p2T, p1T),
                                                                         np.subtract(p2T, p1T))


def calculateS(p1: dict, p2: dict, d: float) -> dict:
    p1T = (p1['x'], p1['y'])
    p2T = (p2['x'], p2['y'])
    sT = np.add(p1T, d * np.subtract(p2T, p1T))
    return {"x": sT[0], "y": sT[1]}


def calculateDistance(p1: dict, p2: dict, location: dict) -> list:
    d = calculateD(location, p1, p2)
    point = {"x": -1, "y": -1}
    if d <= 0:
        point = {"x": p1['x'], "y": p1['y']}
    elif d >= 1:
        point = {"x": p2['x'], "y": p2['y']}
    else:
        point = calculateS(p1, p2, d)

    distance = euclideanDistance(location, point)
    return [point, distance]


def isEqual(point1: dict, point2: dict):
    # node coordinates and way point coordinates differ after 2 decimal places.
    return round(point1['x'], 2) == round(point2['x'], 2) and round(point1['y'], 2) == round(point2['y'], 2)
