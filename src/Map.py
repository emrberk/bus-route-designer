import json
import uuid
from queue import PriorityQueue
from src.util import Utils

FILE_PATH = 'maps/map.json'
JSON_STR = ''


class Map:
    def __init__(self, path=FILE_PATH, jsonStr=JSON_STR):
        file = open(path)
        data = json.load(file)
        file.close()
        self.nodes = data['nodes']
        self.ways = data['ways']
        self.edges = data['edges']
        self.stops = {}
        for key in self.nodes:
            if key not in self.edges:
                self.edges[key] = []

        # way in edges are int, edges are indexed with string
        # in order to prevent duality...
        for key, val in self.edges.items():
            for index, edge in enumerate(val):
                currentEdge = self.edges[key][index]
                self.edges[key][index] = {
                    "to": currentEdge["to"],
                    "way": str(currentEdge["way"]),
                    "speed": currentEdge["speed"]
                }

        # To prevent extra checks for symmetric ways, put them in edges as well
        for key, val in self.edges.items():
            for index, edge in enumerate(val):
                currentEdge = self.edges[key][index]
                if len(list(filter(lambda x: x["to"] == key, self.edges[currentEdge['to']]))) == 0:
                    self.edges[currentEdge['to']].append({
                        "to": key,
                        "way": currentEdge["way"],
                        "speed": currentEdge["speed"]
                    })

        # Will be useful
        self.edgeCosts = {}
        for src, edges in self.edges.items():
            self.edgeCosts[src] = {}
            for edge in edges:
                self.edgeCosts[src][edge["to"]] = {
                    "time": self.getWayTime(edge['way']),
                    "length": self.getWayLength(edge['way']),
                    "wayNo": edge['way']
                }

    def setStop(self, stopId: uuid.UUID, stop: dict):
        self.stops[stopId] = stop

    def getStop(self, stopId: uuid.UUID):
        return self.stops[stopId]

    def delStop(self, stopId: uuid.UUID):
        self.stops.pop(stopId)
        return stopId

    def getWayLength(self, wayNo: str) -> float:
        way = self.ways[wayNo]
        totalLength = 0
        for i in range(0, len(way) - 1):
            totalLength += Utils.euclideanDistance(way[i], way[i + 1])
        return totalLength

    def getWaySpeed(self, wayNo):
        for src, edges in self.edges.items():
            for edge in edges:
                if edge['way'] == wayNo:
                    return edge['speed']

    def getWayTime(self, wayNo):
        return self.getWayLength(wayNo) / self.getWaySpeed(wayNo)

    def getNeighbors(self, node):
        neighbors = []
        for x in self.edges[node]:
            neighbors.append(x["to"])
        return neighbors

    def shortest(self, node1: str, node2: str) -> list:
        time = {}
        length = {}
        prev = {}
        way = {}
        inQ = {}
        q = PriorityQueue()
        for x in self.nodes:
            time[x] = float('inf')
            length[x] = float('inf')
            prev[x] = None
            way[x] = None
            if x != node1:
                q.put((float('inf'), x))
            else:
                q.put((0, x))
            inQ[x] = True
        time[node1] = 0
        length[node1] = 0

        while not q.empty():
            u = q.get()
            if u[1] == node2:
                break
            inQ[u[1]] = False
            neighborsInQ = list(filter(lambda n: inQ[n], self.getNeighbors(u[1])))
            for neighbor in neighborsInQ:
                newTime = time[u[1]] + self.edgeCosts[u[1]][neighbor]['time']
                newLength = length[u[1]] + self.edgeCosts[u[1]][neighbor]['length']
                newWayNo = self.edgeCosts[u[1]][neighbor]['wayNo']
                if newTime < time[neighbor]:
                    q.put((newTime, neighbor))
                    time[neighbor] = newTime
                    length[neighbor] = newLength
                    way[neighbor] = newWayNo
                    prev[neighbor] = u[1]
        path = []
        totalWay = []
        current = node2
        while current is not None:
            path = [current] + path
            totalWay = [way[current]] + totalWay if way[current] is not None else totalWay
            current = prev[current]
        return [totalWay, time[node2], length[node2]]

    def getPointPercentage(self, point: dict, wayNo: str, segmentStart: int) -> float:
        way = self.ways[wayNo]
        # Calculate the distance until current segment
        lengthBeforeCurrent = 0
        if segmentStart > 0:
            for i in range(0, segmentStart):
                lengthBeforeCurrent += Utils.euclideanDistance(way[i], way[i + 1])
        # Calculate the distance from segment start to our point
        lengthInCurrent = Utils.euclideanDistance(way[segmentStart], point)
        lengthFromStart = lengthBeforeCurrent + lengthInCurrent
        totalLength = self.getWayLength(wayNo)
        return (lengthFromStart / totalLength) * 100

    def closestedge(self, location: dict) -> list:
        result = {
            'edgeId': '',
            "distance": float('inf'),
            "closestPoint": {"x": 0, "y": 0},
            "percentage": 0
        }
        for wayNo, way in self.ways.items():
            for i in range(0, len(way) - 1):
                [closestPoint, distance] = Utils.calculateDistance(way[i], way[i + 1], location)
                if distance < result['distance']:
                    result['distance'] = distance
                    result['edgeId'] = wayNo
                    result['closestPoint'] = closestPoint
                    percentage = self.getPointPercentage(closestPoint, wayNo, i)
                    result['percentage'] = percentage

        return [result['edgeId'], result['closestPoint'], result['percentage'], result['distance']]

    def addstop(self, edgeId: str, direction: bool, percentage: float, description: str) -> uuid.UUID:
        givenEdge = self.ways[edgeId]
        directedEdge = givenEdge if direction else givenEdge[::-1]
        totalLength = self.getWayLength(edgeId)
        desiredLength = (totalLength * percentage) / 100

        currentLength = 0
        for i in range(0, len(directedEdge) - 1):
            segmentLength = Utils.euclideanDistance(directedEdge[i], directedEdge[i + 1])
            if desiredLength > segmentLength + currentLength:
                currentLength += segmentLength
            else:
                lengthInCurrentSegment = desiredLength - currentLength
                d = lengthInCurrentSegment / segmentLength
                point = Utils.calculateS(directedEdge[i], directedEdge[i + 1], d)
                stopId = uuid.uuid4()
                self.setStop(stopId, {
                    "id": stopId,
                    "x": point['x'],
                    "y": point['y'],
                    "source": directedEdge[0],
                    "destination": directedEdge[-1],
                    "description": description
                })
                return stopId

    def stopdistance(self, stop1Id: uuid.UUID, stop2Id: uuid.UUID) -> float:
        if stop1Id == stop2Id:
            return 0
        stop1 = self.stops[stop1Id]
        stop2 = self.stops[stop2Id]
        stop1Target = ''
        stop2Source = ''
        for nodeNumber, nodeCoordinates in self.nodes.items():
            if Utils.isEqual(nodeCoordinates, stop1['destination']):
                stop1Target = nodeNumber
            if Utils.isEqual(nodeCoordinates, stop2['source']):
                stop2Source = nodeNumber

        distanceBetweenNodes = self.shortest(stop1Target, stop2Source)[2]
        walk1 = Utils.euclideanDistance({"x": stop1['x'], "y": stop1['y']}, self.nodes[stop1Target])
        walk2 = Utils.euclideanDistance({"x": stop2['x'], "y": stop2['y']}, self.nodes[stop2Source])
        return distanceBetweenNodes + walk1 + walk2

    def shorteststop(self, location: dict) -> uuid.UUID:
        shortestId = ''
        minDistance = float('inf')
        for stopId, stopVal in self.stops:
            distance = Utils.euclideanDistance({"x": stopVal['x'], "y": stopVal['y']}, location)
            if distance < minDistance:
                shortestId = stopId
                minDistance = distance
        return shortestId
