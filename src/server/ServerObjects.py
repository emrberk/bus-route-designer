import threading
from queue import Queue

from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.user.User import User
from src.server.ServerFunctions import *

PATH = '../../maps/map.json'


class ServerObjects:
    class ByServer:
        addresses = []
        threads = []
        users = []
        schedules = []
        lines = []
        notifications = {}
        maps = [Map(PATH)]
        s1 = maps[0].addstop('1', True, 100, 't1')
        s2 = maps[0].addstop('2', True, 100, 't2')
        s3 = maps[0].addstop('3', True, 100, 't3')
        schedules.append(Schedule(maps[0]))
        schedules[0].newroute(Route([s1, s2, s3]))


    class ByThread:
        scheduleLock = threading.Lock()
        routeLock = threading.Lock()
        mapLock = threading.Lock()
        lineLock = threading.Lock()

    class ByUser:
        users = [User("def", "def@gmail.com", "default account", "1234")]
