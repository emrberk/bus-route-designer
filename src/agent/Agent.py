import json
import queue
import threading

from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.agent.AgentEnum import AgentEnum as ae
from src.agent.NotificationHandler import NotificationHandler
from src.server.ServerObjects import ServerObjects
from src.util.Utils import getUtfPackage


class Agent(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.selectedMapId = 0
        self.selectedMap = Map()
        self.attachedSchedules = []
        self.messageQueue = queue.Queue()
        self.daemon = True
        self._stop_event = threading.Event()
        self.notificationHandler = NotificationHandler(conn, addr)

    def stop(self):
        self._stop_event.set()

    def login(self):
        while True:
            try:
                self.conn.sendall("Please login to system :\n".encode())
                self.conn.sendall("Username : ".encode())
                usrname = self.conn.recv(1024)
                usrname = getUtfPackage(usrname)
                names = [usr.username for usr in ServerObjects.ByUser.users]
                if usrname not in names:
                    self.conn.sendall(f"No user with username {usrname}\n".encode())
                    continue
                index = names.index(usrname)
                self.conn.sendall("Password : ".encode())
                passwd = self.conn.recv(1024)
                passwd = getUtfPackage(passwd)
                user = ServerObjects.ByUser.users[index]
                token = user.login(passwd)
                if token:
                    return True
            except Exception as e:
                self.conn.sendall(str(e).encode())
                self.conn.close()

    def run(self):
        self.notificationHandler.start()
        print(f'Client {self.addr} is connected.')
        self.login()
        while not self._stop_event.is_set():
            self.conn.sendall("What do you want me to do? : \n".encode())
            response = self.conn.recv(1024)
            response = response.decode().split()
            if response[0] == ae.ADD_SCHEDULE:
                ServerObjects.ByThread.addScheduleLock.acquire()
                created_map = Map(response[1])
                schedule = Schedule(created_map)
                ServerObjects.ByServer.schedules.append(schedule)
                ServerObjects.ByServer.notificationQueue.put(
                    f"Thread {threading.get_ident()} added a new schedule on Map")
                ServerObjects.ByThread.addScheduleLock.release()

            if response[0] == ae.ADD_MAP:
                ServerObjects.ByThread.addMapLock.acquire()
                created_map = Map(response[1])
                ServerObjects.ByServer.maps.append(created_map)
                ServerObjects.ByServer.notificationQueue.put(
                    f"Thread {threading.get_ident()} added a new schedule on Map")
                ServerObjects.ByThread.addMapLock.release()

            if response[0] == ae.SHOW_ALL_THREADS:
                json_data = json.dumps(ServerObjects.ByServer.addresses)
                message_bytes = json_data.encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            if response[0] == ae.LIST_MAPS:
                mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
                mapIds = list(set(mapIds))
                message_bytes = ' '.join(mapIds).encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            # ----------- open map functions ------------------
            if response[0] == ae.OPEN_MAP:
                mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
                mapIds = list(set(mapIds))
                if response[1] in mapIds:
                    self.selectedMapId = int(response[1])
                    for schedule in ServerObjects.ByServer.schedules:
                        print(f"sched id : {schedule.map.id}")
                        print(f"map id : {self.selectedMapId}")
                        if schedule.map.id == self.selectedMapId:
                            self.attachedSchedules.append(schedule)
                    index = mapIds.index(response[1])
                    self.selectedMap = ServerObjects.ByServer.maps[index]
                    message_bytes = f"Map with id {self.selectedMapId} is opened".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())

            if response[0] == ae.CLOSE_MAP:
                self.selectedMapId = 0
                self.selectedMap = None
                self.attachedSchedules = []
                message_bytes = f"Map is closed".encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            if response[0] == ae.LIST_SCHEDULES:
                schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                schedIds = list(set(schedIds))
                message_bytes = ' '.join(schedIds).encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            if response[0] == ae.LIST_STOPS:
                stops = self.selectedMap.getStopsInfo()
                message_bytes = str(stops).encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            if response[0] == ae.LIST_ROUTES:
                schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                index = schedIds.index(response[1])
                schedule_edited = self.attachedSchedules[index]
                routes = schedule_edited.listroutes()
                message_bytes = str(routes).encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())

            if response[0] == ae.ADD_ROUTE:
                # TODO : bura yarım devam ediyorum
                ServerObjects.ByThread.addRouteLock.acquire()
                schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                index = schedIds.index(response[1])
                schedule_edited = self.attachedSchedules[index]
                stoplist = []
                for i in range(int(response[2])):
                    stoplist.append(response[3 + i])
                schedule_edited.newroute([Route(stoplist)])
                message_bytes = "New route is added.".encode()
                self.conn.sendall(message_bytes)
                self.conn.send("\n".encode())
