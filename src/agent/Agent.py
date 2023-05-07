import queue
import threading
from uuid import UUID

from src.Line import Line
from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.agent.AgentEnum import AgentEnum as ae
from src.agent.NotificationHandler import NotificationHandler
from src.server.ServerObjects import ServerObjects
from src.util.Utils import *


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
            try:
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
                    message_bytes = concat(routes).encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())

                if response[0] == ae.ADD_ROUTE:
                    ServerObjects.ByThread.addRouteLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    stoplist = []
                    for i in range(int(response[2])):
                        stoplist.append(UUID(response[3 + i]))
                    schedule_edited.newroute([Route(stoplist)])
                    message_bytes = "New route is added.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addRouteLock.release()

                if response[0] == ae.UP_ROUTE:
                    ServerObjects.ByThread.addRouteLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    route_edited = int(response[2])
                    stoplist = []
                    for i in range(int(response[3])):
                        stoplist.append(UUID(response[4 + i]))
                    schedule_edited.updateroute(route_edited, stoplist)
                    message_bytes = f"Route with id {route_edited} is updated.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addRouteLock.release()

                if response[0] == ae.DEL_ROUTE:
                    ServerObjects.ByThread.addRouteLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    schedule_edited.delroute(int(response[2]))
                    message_bytes = f"Route with id {int(response[2])} is deleted.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addRouteLock.release()

                if response[0] == ae.LIST_LINES:
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    lines = schedule_edited.listlines()
                    message_bytes = concat(lines).encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                # Line(datetime.time(hour=14, minute=30), datetime.time(hour=20), datetime.time(minute=30),
                #                                    self.schedule.getroute(1), "ilk line")
                if response[0] == ae.ADD_LINE:
                    ServerObjects.ByThread.addLineLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    schedule_edited.addLine(Line(datetime.time(hour=int(response[2]), minute=int(response[3])),
                                                 datetime.time(hour=int(response[4]), minute=int(response[5])),
                                                 datetime.time(minute=int(response[6])),
                                                 schedule_edited.getroute(int(response[7])), response[8]))
                    message_bytes = "New line is added.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addLineLock.release()

                if response[0] == ae.UP_LINE:
                    ServerObjects.ByThread.addLineLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    line_edited = int(response[2])
                    schedule_edited.updateLine(datetime.time(hour=int(response[3]), minute=int(response[4])),
                                               datetime.time(hour=int(response[5]), minute=int(response[6])),
                                               datetime.time(minute=int(response[7])),
                                               schedule_edited.getroute(int(response[8])), response[9])
                    message_bytes = f"Line with id {line_edited} is updated.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addLineLock.release()

                if response[0] == ae.DEL_LINE:
                    ServerObjects.ByThread.addLineLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    schedule_edited.delLine(int(response[2]))
                    message_bytes = f"Line with id {int(response[2])} is deleted.".encode()
                    self.conn.sendall(message_bytes)
                    self.conn.send("\n".encode())
                    ServerObjects.ByThread.addRouteLock.release()

            except Exception as e:
                self.conn.sendall(str(e).encode())
