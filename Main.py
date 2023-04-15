from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.Line import Line
import datetime

if __name__ == '__main__':
    m = Map()
    print(f"type of : {type(m.edges)}")
    print(f"ways : {m.ways}")
    print(f"edges : {m.edges}")
    stopId1 = m.addstop('0', False, 0.0, 'test1')
    stopId2 = m.addstop('41', True, 100, 'test2')
    s1 = m.addstop('1', True, 100, 't1')
    s2 = m.addstop('2', True, 100, 't2')
    s3 = m.addstop('3', True, 100, 't3')
    print(f"stops : {m.stops}")
    print(f"stop distance : {m.stopdistance(stopId1, stopId1)}")
    print(f"shortest btw 0 and 32 -> {m.shortest('0', '32')}")
    s = Schedule(m)
    s.newroute([Route([s1, s2, s3])])
    print(f"stop description : {s.getStopDescr(s.getroute(1), 0)}")
    line = Line(datetime.time(hour=14, minute=30), datetime.time(hour=20), datetime.time(minute=30),
                s.getroute(1), "ilk line")
    s.addLine(line)
    s.lineinfo(1)
    s.stopinfo(s1)
