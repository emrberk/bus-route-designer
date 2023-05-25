import numpy as np
import json

class Point:
    def __init__(self, *args):
        # initialize with x and y coordinates
        if len(args) == 2:
            self.x = args[0]
            self.y = args[1]
        # initialize with dict {"x", "y"}
        elif type(args[0]) is dict:
            self.x = args[0]['x']
            self.y = args[0]['y']
        # initialize with ndarray
        else:
            self.x = args[0][0]
            self.y = args[0][1]

        self._fields = ('x', 'y')

    def __iter__(self):
        for f in self._fields:
            yield getattr(self, f)

    def __sub__(self, p2):
        return Point(np.subtract((self.x, self.y), (p2.x, p2.y)))

    def __add__(self, p2):
        return Point(np.add((self.x, self.y), (p2.x, p2.y)))

    def __mul__(self, scalar):
        return Point(np.dot((self.x, self.y), scalar))

    def __eq__(self, other):
        return round(self.x, 2) == round(other.x, 2) and round(self.y, 2) == round(other.y, 2)

    def get(self):
        return {
            'x': self.x,
            'y': self.y
        }

    def __str__(self):
        return json.dumps(self.get())

    __repr__ = __str__

