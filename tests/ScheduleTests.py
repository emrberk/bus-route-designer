import datetime
import unittest

from src.Exception.LineException import LineDeletedException
from src.Exception.RouteException import *
from src.Line import Line
from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule


class ScheduleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.defaultMap = Map(path="../maps/map.json")
        self.schedule = Schedule(self.defaultMap)
        s1 = self.defaultMap.addstop('1', True, 100, 't1')
        s2 = self.defaultMap.addstop('2', True, 100, 't2')
        s3 = self.defaultMap.addstop('3', True, 100, 't3')
        self.stop1 = s1
        self.stop2 = s2
        self.stop3 = s3
        self.schedule.newroute(Route([s1, s2, s3]))
        self.schedule.addLine(Line(datetime.time(hour=14, minute=30), datetime.time(hour=20), datetime.time(minute=30),
                                   self.schedule.getroute(1), "ilk line"))

    def test_init(self):
        self.assertEqual(len(self.schedule.lines), 1, "(init) : Line count")
        self.assertEqual(len(self.schedule.routes), 1, "(init) : Route count")
        self.assertEqual(len(self.schedule.routes[0].stops), 3, "(init) : Stop count")
        self.assertNotEqual(self.schedule.map, None, "(init) : Map is not null test")

    def test_NewRoute(self):
        createdRoute = self.schedule.newroute(Route([self.stop1, self.stop3]))
        self.assertEqual(createdRoute.id, 2, "(newRoute) : route counter test")
        self.assertEqual(len(createdRoute.stops), 2, "(newRoute) : route stops test")
        self.assertEqual(createdRoute.stops, [self.stop1, self.stop3], "(newRoute) : route stops test")
        self.assertEqual(len(self.schedule.routes), 2, "(newRoute) : schedule.route count test")

    def test_getRoute(self):
        self.assertEqual(self.schedule.getroute(1), self.schedule.routes[0], "(getRoute) : default test")
        self.schedule.delroute(1)
        with self.assertRaises(RouteDeletedException):
            self.schedule.getroute(0)

    def test_updateRoute(self):
        self.schedule.updateroute(1, [self.stop2, self.stop3, self.stop1])
        self.assertEqual(len(self.schedule.routes), 1, "(updateRoute) : Route count")
        self.assertEqual(len(self.schedule.routes[0].stops), 3, "(updateRoute) : stop count test")
        self.assertNotEqual(self.schedule.routes[0].stops, [self.stop1, self.stop2, self.stop3],
                            "(updateRoute) : wrong order test")
        self.assertEqual(self.schedule.routes[0].stops, [self.stop2, self.stop3, self.stop1],
                         "(updateRoute) : true order test")

    def test_delRoute(self):
        self.schedule.delroute(1)
        self.assertEqual(len(self.schedule.routes), 1, "Route count after deletion test")
        self.assertFalse(self.schedule.routes[0].active, "Route count after deletion test")
        with self.assertRaises(RouteDeletedException):
            self.schedule.delroute(1)

    def test_addLine(self):
        self.assertEqual(len(self.schedule.lines), 1)
        self.schedule.addLine(Line(datetime.time(hour=20), datetime.time(hour=22), datetime.time(minute=30),
                                   self.schedule.getroute(1), "second line"))
        self.assertEqual(len(self.schedule.lines), 2, "Line count after addition test")
        self.assertEqual(self.schedule.lines[1].description, "second line", "description test")

    def test_getLine(self):
        self.assertEqual(self.schedule.getLine(1).description, "ilk line", "descr test")

    def test_updateLine(self):
        self.assertEqual(self.schedule.getLine(1).start_time, datetime.time(hour=14, minute=30))
        self.assertEqual(self.schedule.getLine(1).end_time, datetime.time(hour=20))
        self.assertEqual(self.schedule.getLine(1).description, "ilk line", "descr test")
        self.schedule.updateLine(1, datetime.time(hour=17, minute=30), datetime.time(hour=21), datetime.time(minute=15),
                                 self.schedule.getroute(1), "ilk line updated")
        self.assertEqual(self.schedule.getLine(1).start_time, datetime.time(hour=17, minute=30),
                         "start_time after update")
        self.assertEqual(self.schedule.getLine(1).end_time, datetime.time(hour=21), "end_time after update")
        self.assertEqual(self.schedule.getLine(1).description, "ilk line updated", "descr test after update")

    def test_delLine(self):
        self.schedule.delLine(1)
        self.assertEqual(len(self.schedule.lines), 1, "length check")
        self.assertFalse(self.schedule.lines[0].active, "Line active after deletion test")
        with self.assertRaises(LineDeletedException):
            self.schedule.delLine(1)

    def test_calculateEstimatedTime(self):
        expected = [datetime.time(15, 5, 59),
                    datetime.time(15, 35, 59),
                    datetime.time(16, 5, 59),
                    datetime.time(16, 35, 59),
                    datetime.time(17, 5, 59),
                    datetime.time(17, 35, 59),
                    datetime.time(18, 5, 59),
                    datetime.time(18, 35, 59),
                    datetime.time(19, 5, 59),
                    datetime.time(19, 35, 59),
                    datetime.time(20, 5, 59)]
        time = self.schedule.calculateEstimatedTimes(1, self.schedule.routes[0].stops[1])
        self.assertEqual(expected, time, "Estimated Time Test")


if __name__ == '__main__':
    unittest.main()
