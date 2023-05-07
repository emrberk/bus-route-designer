import threading

from queue import Queue
from src.Map import Map
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

    class ByThread:
        addScheduleLock = threading.Lock()
        addMapLock = threading.Lock()

    class ByUser:
        users = [User("def", "def@gmail.com", "default account", "1234")]
