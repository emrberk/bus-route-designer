import threading

from queue import Queue
from src.Map import Map
from src.Schedule import Schedule
from src.user.User import User

PATH = '../../maps/map.json'


class ServerObjects:
    class ByServer:
        notificationQueue = Queue()
        addresses = []
        threads = []
        users = []
        schedules = []
        maps = [Map(PATH)]
        s1 = maps[0].addstop('1', True, 100, 't1')
        s2 = maps[0].addstop('2', True, 100, 't2')
        s3 = maps[0].addstop('3', True, 100, 't3')
        schedules.append(Schedule(maps[0]))

    class ByThread:
        addScheduleLock = threading.Lock()
        addRouteLock = threading.Lock()
        addMapLock = threading.Lock()

    class ByUser:
        users = [User("def", "def@gmail.com", "default account", "1234")]
