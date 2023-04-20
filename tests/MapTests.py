import unittest

from src.Map import Map
from src.Point import Point


# Örnek test sınıfı
class TestMapFunctions(unittest.TestCase):

    def setUp(self) -> None:
        self.defaultMap = Map(path="../maps/map.json")
        s1 = self.defaultMap.addstop('1', True, 100, 't1')
        s2 = self.defaultMap.addstop('2', True, 100, 't2')
        s3 = self.defaultMap.addstop('3', True, 100, 't3')
        self.stop1 = s1
        self.stop2 = s2
        self.stop3 = s3

    # Test methods
    def test_init(self):
        self.assertEqual(len(self.defaultMap.stops), 3, "Stop count")
        self.assertEqual(len(self.defaultMap.edges), 42, "Edge Count")
        self.assertEqual(len(self.defaultMap.nodes), 42, "Node Count")
        self.assertEqual(len(self.defaultMap.ways), 55, "Way Count")

    def test_getStop(self):
        stop = self.defaultMap.getStop(self.stop1)
        self.assertEqual(stop.id, self.stop1, "Stop id test")
        self.assertEqual(stop.point, Point(35.279578, 270.2991), "Stop point test")
        self.assertEqual(stop.source, '2', "Source test")
        self.assertEqual(stop.destination, '1', "Destination test")
        self.assertEqual(stop.description, "t1", "Description test")
        self.assertEqual(stop.wayId, '1', "WayId test")

    def test_delStop(self):
        deleted = self.defaultMap.delStop(self.stop2)
        self.assertEqual(len(self.defaultMap.stops), 2, "Stop deletion test")
        with self.assertRaises(KeyError):
            self.defaultMap.getStop(self.stop2)

    def test_getWayLength(self):
        self.assertEqual(self.defaultMap.getWayLength("1"), 59.00122396008631, "WayLength test")

    def test_getWaySpeed(self):
        self.assertEqual(self.defaultMap.getWaySpeed("1"), 30, "WaySpeed test")

    def test_getWayTime(self):
        self.assertEqual(self.defaultMap.getWayTime("1"), 1.9667074653362102, "WaySpeedTest")

    def test_getNeighbours(self):
        neighbours = self.defaultMap.getNeighbors("1")
        neighbourList = ['0', '2', '9']
        self.assertEqual(neighbours, neighbourList, "Neighbour test")

    def test_shortest(self):
        shortestTuple = (['1', '2', '7', '6', '5'], 4.335181209608294, 130.0554362882488)
        self.assertEqual(self.defaultMap.shortest('1', '5'), shortestTuple, "Shortest Test")

    def test_closestEdge(self):
        closestEdge = ['37', Point(4.4012355, 91.13348), 0.0, 88.19908559524221]
        self.assertEqual(self.defaultMap.closestedge(Point(1, 3)), closestEdge, "Closest Edge Test")

    def test_addStop(self):
        testStop = self.defaultMap.addstop('4', True, 50, 'testStop')
        stop = self.defaultMap.getStop(testStop)
        self.assertEqual(len(self.defaultMap.stops), 4, "(addStop) : Stop count test for addStop")
        self.assertEqual(stop.id, testStop, "(addStop) : Stop id test")
        self.assertEqual(stop.point, Point(63.476512, 156.70955), "(addStop) : Stop point test")
        self.assertEqual(stop.source, '5', "(addStop) : Source test")
        self.assertEqual(stop.destination, '3', "(addStop) : Destination test")
        self.assertEqual(stop.description, "testStop", "(addStop) : Description test")
        self.assertEqual(stop.wayId, '4', "(addStop) : WayId test")

    def test_stopDistance(self):
        self.assertEqual(self.defaultMap.stopdistance(self.stop1, self.stop1), (0, 0),
                         "(stopDistance) : should be zero case")
        self.assertEqual(self.defaultMap.stopdistance(self.stop1, self.stop3), (232.17721480878328, 7.739240493626109),
                         "(stopDistance) : normal case")

    def test_shortestStop(self):
        self.assertEqual(self.defaultMap.shorteststop(Point(0, 0)), self.stop3,
                         "(shortestStop) : standart Case")


if __name__ == '__main__':
    unittest.main()
