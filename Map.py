import json
import math

FILE_PATH = './map.json'
JSON_STR = ''

class Map:
    def __init__(self, path=FILE_PATH, jsonStr=JSON_STR):
        file = open(path)
        data = json.load(file)
        file.close()
        self.nodes = data['nodes']
        self.ways = data['ways']
        self.edges = data['edges']
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

    def getWayLength(self, way):
        totalLength = 0
        for i in range(0, len(way) - 1):
            totalLength += math.sqrt((way[i]['x'] - way[i + 1]['x']) ** 2 + (way[i]['y'] - way[i + 1]['y']) ** 2)
        return totalLength

    def shortest(self, node1, node2):
        edges1to2 = list(filter(lambda edge: edge['to'] == node2, self.edges[node1]))
        edges2to1 = list(filter(lambda edge: edge['to'] == node1, self.edges[node2]))
        edgesBetween = edges1to2 + edges2to1
        min = []
        for edge in edgesBetween:
            way = self.ways[edge['way']]
            wayLength = self.getWayLength(way)
            tripTime = wayLength / edge['speed']
            if len(min) == 0 or tripTime < min[2]:
                min = [edge['way'], wayLength, tripTime]
        return min


if __name__ == '__main__':
    m = Map()
    print(m.shortest('25', '22'))

