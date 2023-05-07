import json
import queue
import threading

from src.Map import Map
from src.Schedule import Schedule
from src.agent.AgentEnum import AgentEnum as ae
from src.server.ServerObjects import ServerObjects


class Agent(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.messageQueue = queue.Queue()
        self.daemon = True
        self._stop_event = threading.Event()
        self.newMessage = threading.Event()

    def stop(self):
        self._stop_event.set()

    def login(self):
        while True:
            try:
                self.conn.sendall("Please login to system :\n".encode())
                self.conn.sendall("Username : ".encode())
                usrname = self.conn.recv(1024)
                usrname = usrname.decode('utf-8')
                usrname = usrname.replace("\r", "").replace("\n", "")
                names = [usr.username for usr in ServerObjects.ByUser.users]
                if usrname not in names:
                    self.conn.sendall(f"No user with username {usrname}\n".encode())
                    continue
                index = names.index(usrname)
                self.conn.sendall("Password : ".encode())
                passwd = self.conn.recv(1024)
                passwd = passwd.decode('utf-8')
                passwd = passwd.replace("\r", "").replace("\n", "")
                user = ServerObjects.ByUser.users[index]
                token = user.login(passwd)
                if token:
                    return True
            except Exception as e:
                ex_str = str(e)
                self.conn.sendall(ex_str.encode())

    def run(self):
        print(f'Client {self.addr} is connected.')
        self.login()
        while not self._stop_event.is_set():
            message = "What do you want me to do? : \n"
            message_bytes = message.encode()
            self.conn.sendall(message_bytes)
            data = self.conn.recv(1024)
            response = data.decode()
            response = response.split()
            if self.newMessage.is_set():
                print(self.messageQueue.get())
            if response[0] == ae.ADD_SCHEDULE:
                ServerObjects.ByThread.addScheduleLock.acquire()
                created_map = Map(response[1])
                schedule = Schedule(created_map)
                ServerObjects.ByServer.schedules.append(schedule)
                self.messageQueue.put(f"Thread {threading.get_ident()} added a new schedule on Map")
                self.newMessage.set()
                ServerObjects.ByThread.addScheduleLock.release()
            if response[0] == ae.ADD_MAP:
                ServerObjects.ByThread.addMapLock.acquire()
                created_map = Map(response[1])
                ServerObjects.ByServer.maps.append(created_map)
                self.messageQueue.put(f"Thread {threading.get_ident()} added a new schedule on Map")
                self.newMessage.set()
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
