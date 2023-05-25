import uuid
from src.Point import Point
import json

class BusStop:
    def __init__(self, id: uuid.UUID, point: Point, source: str, destination: str, description: str, wayId: str):
        self.id = id
        self.point = point
        self.source = source
        self.destination = destination
        self.description = description
        self.wayId = wayId

    def getId(self) -> uuid.UUID:
        return self.id

    def setId(self, id: uuid.UUID):
        self.id = id

    def getWayId(self) -> str:
        return self.wayId

    def setWayId(self, wayId: str):
        self.wayId = wayId

    def getPoint(self) -> Point:
        return self.point

    def setPoint(self, point: Point):
        self.point = point

    def getSource(self) -> str:
        return self.source

    def setSource(self, source: Point):
        self.source = source

    def getDestination(self) -> str:
        return self.destination

    def setDestination(self, destination: str):
        self.destination = destination

    def getDescription(self) -> str:
        return self.description

    def setDescription(self, description: str):
        self.description = description

    def get(self):
        return {
            'id': self.id,
            'point': self.point.get(),
            'source': self.source,
            'destination': self.destination,
            'description': self.description,
            'wayId': self.wayId
        }

    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

