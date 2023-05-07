import json
import threading

from src.util import Utils
from src.Map import Map
from src.Schedule import Schedule
from src.agent.AgentEnum import AgentEnum as ae
from src.agent.NotificationHandler import NotificationHandler
from src.server.ServerObjects import ServerObjects


class Agent(threading.Thread):
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.daemon = True
        self._stop_event = threading.Event()
        self.notificationHandler = NotificationHandler(conn, addr)
        super().__init__()

    def stop(self):
        self._stop_event.set()

    def login(self):
        while True:
            try:
                Utils.sendDataAsChunks(self.conn, "Please login to system :\n")
                Utils.sendDataAsChunks(self.conn, "Username : ")
                usrname = Utils.getDataAsChunks(self.conn)
                names = [usr.username for usr in ServerObjects.ByUser.users]
                if usrname not in names:
                    Utils.sendDataAsChunks(self.conn, f"No user with username {usrname}\n")
                    continue
                index = names.index(usrname)
                Utils.sendDataAsChunks(self.conn, "Password : ")
                passwd = Utils.getDataAsChunks(self.conn)
                user = ServerObjects.ByUser.users[index]
                token = user.login(passwd)
                if token:
                    return True
            except Exception as e:
                Utils.sendDataAsChunks(self.conn, e)
                self.conn.close()

    def run(self):
        self.notificationHandler.start()
        print(f'Client {self.addr} is connected.')
        self.login()
        while not self._stop_event.is_set():
            Utils.sendDataAsChunks(self.conn, "What do you want me to do? : \n")

            response = Utils.getDataAsChunks(self.conn)
            response = response.split()
            if response[0] == ae.ADD_SCHEDULE:
                ServerObjects.ByThread.addScheduleLock.acquire()
                created_map = Map(response[1])
                schedule = Schedule(created_map)
                ServerObjects.ByServer.schedules.append(schedule)
                ServerObjects.ByServer.notificationQueue.put(f"Thread {threading.get_ident()} added a new schedule on Map")
                ServerObjects.ByThread.addScheduleLock.release()
            if response[0] == ae.ADD_MAP:
                ServerObjects.ByThread.addMapLock.acquire()
                created_map = Map(response[1])
                ServerObjects.ByServer.maps.append(created_map)
                ServerObjects.ByServer.notificationQueue.put(f"Thread {threading.get_ident()} added a new schedule on Map")
                ServerObjects.ByThread.addMapLock.release()
            if response[0] == ae.SHOW_ALL_THREADS:
                json_data = json.dumps(ServerObjects.ByServer.addresses)
                Utils.sendDataAsChunks(self.conn, json_data + '\n')
            if response[0] == ae.LIST_MAPS:
                mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
                mapIds = list(set(mapIds))
                message = ' '.join(mapIds)
                Utils.sendDataAsChunks(self.conn, message + '\n')
