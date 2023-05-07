import heapq
import json
import uuid

from src.BusStop import BusStop
from src.Exception.ErrorCodes import ErrorCodes
from src.Exception.StopException import StopNotFoundException
from src.Point import Point
from src.util import Utils

FILE_PATH = '../../maps/map.json'
JSON_STR = ''


class Map:
    counter = 0

    def __init__(self, path=FILE_PATH, jsonStr=JSON_STR):
        Map.counter += 1
        self.id = Map.counter
        data = {}
        if not len(jsonStr):
            file = open(path)
            data = json.load(file)
            file.close()
        else:
            data = json.loads(jsonStr)

        self.nodes = {}
        for nodeNo, nodeVal in data['nodes'].items():
            self.nodes[nodeNo] = Point(nodeVal)

        self.ways = {}
        for wayNo, wayVal in data['ways'].items():
            self.ways[wayNo] = []
            for pt in data['ways'][wayNo]:
                self.ways[wayNo].append(Point(pt))

        self.stops = {}

        self.edges = data['edges']
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
                    "speed": currentEdge["speed"],
                    "symmetric": False
                }

        # To prevent extra checks for symmetric ways, put them in edges as well
        for key, val in self.edges.items():
            for index, edge in enumerate(val):
                currentEdge = self.edges[key][index]
                if len(list(filter(lambda x: x["to"] == key, self.edges[currentEdge['to']]))) == 0:
                    self.edges[currentEdge['to']].append({
                        "to": key,
                        "way": currentEdge["way"],
                        "speed": currentEdge["speed"],
                        "symmetric": True
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

    def setStop(self, stopId: uuid.UUID, stop: BusStop):
        self.stops[stopId] = stop

    def getStop(self, stopId: uuid.UUID):
        if self.stops[stopId]:
            return self.stops[stopId]
        else:
            raise StopNotFoundException(ErrorCodes.ByStop.STOP_NOT_FOUND, f"Stop with id {stopId} cannot found.")

    def delStop(self, stopId: uuid.UUID):
        del self.stops[stopId]
        return stopId

    def getWayLength(self, wayNo: str) -> float:
        way = self.ways[wayNo]
        totalLength = 0
        for i in range(0, len(way) - 1):
            totalLength += Utils.euclideanDistance(way[i], way[i + 1])
        return totalLength

    def getWaySpeed(self, wayNo: str) -> float:
        for src, edges in self.edges.items():
            for edge in edges:
                if edge['way'] == wayNo:
                    return edge['speed']

    def getWayTime(self, wayNo: str) -> float:
        return self.getWayLength(wayNo) / self.getWaySpeed(wayNo)

    def getNeighbors(self, node: str) -> [str]:
        neighbors = []
        for x in self.edges[node]:
            neighbors.append(x["to"])
        return neighbors

    def shortest(self, startNode: str, endNode: str):
        distances = {nodeId: float('inf') for nodeId in self.edgeCosts}
        distances[startNode] = 0

        previous_nodes = {nodeId: None for nodeId in self.edgeCosts}

        priority_queue = [(0, startNode)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_node == endNode:
                path = [endNode]
                total_time = distances[endNode]
                total_length = 0

                while previous_nodes[path[0]] is not None:
                    path.insert(0, previous_nodes[path[0]])
                    total_length += self.edgeCosts[path[0]][path[1]]['length']

                return path, total_time, total_length

            if current_distance > distances[current_node]:
                continue

            for neighbor_node, edge_attrs in self.edgeCosts[current_node].items():
                distance_to_neighbor = current_distance + edge_attrs['time']

                if distance_to_neighbor < distances[neighbor_node]:
                    distances[neighbor_node] = distance_to_neighbor
                    previous_nodes[neighbor_node] = current_node
                    heapq.heappush(priority_queue, (distance_to_neighbor, neighbor_node))

        return None, None, None

    def getPointPercentage(self, point: Point, wayNo: str, segmentStart: int) -> float:
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

    def closestedge(self, location: Point) -> list:
        result = {
            'edgeId': '',
            "distance": float('inf'),
            "closestPoint": Point(0, 0),
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
        src = ''
        dest = ''
        for edgeSource, edges in self.edges.items():
            for edge in edges:
                if edge['way'] == edgeId:
                    takeStraight = direction != edge['symmetric']
                    src = edgeSource if takeStraight else edge['to']
                    dest = edge['to'] if takeStraight else edgeSource
                    break
            if len(src) > 0:
                break

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
                stop = BusStop(stopId, point, src, dest, description, edgeId)
                self.setStop(stopId, stop)
                return stopId

    def stopdistance(self, stop1Id: uuid.UUID, stop2Id: uuid.UUID) -> tuple:
        stop1 = self.stops[stop1Id]
        stop2 = self.stops[stop2Id]
        if stop1.getPoint() == stop2.getPoint():
            return 0, 0
        stop1Target = ''
        stop2Source = ''
        for nodeNumber, nodeCoordinates in self.nodes.items():
            if nodeCoordinates == self.nodes[stop1.getDestination()]:
                stop1Target = nodeNumber
            if nodeCoordinates == self.nodes[stop2.getSource()]:
                stop2Source = nodeNumber

        [_, time, distanceBetweenNodes] = self.shortest(stop1Target, stop2Source)
        walk1 = Utils.euclideanDistance(stop1.point, self.nodes[stop1Target])
        walk2 = Utils.euclideanDistance(stop2.point, self.nodes[stop2Source])
        walkTime = (walk1 + walk2) / self.getWaySpeed(stop1.getWayId())
        return distanceBetweenNodes + walk1 + walk2, time + walkTime

    def shorteststop(self, location: Point) -> uuid.UUID:
        shortestId = ''
        minDistance = float('inf')
        for stopId, stopVal in self.stops.items():
            distance = Utils.euclideanDistance(stopVal.getPoint(), location)
            if distance < minDistance:
                shortestId = stopId
                minDistance = distance
        return shortestId

    def getStopsInfo(self):
        if self.stops == {}:
            print("There is no stop in this area.")
        for stop in self.stops:
            print(self.getStop(stop))
