import queue
import threading
from uuid import UUID
import hashlib
from src.Line import Line
from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.agent.AgentEnum import AgentEnum as ae
from src.agent.NotificationHandler import NotificationHandler
from src.agent.HelpCommand import HELP_LIST
from src.server.ServerObjects import ServerObjects
from src.util.Utils import *
import traceback


def putNotification(message):
    for peer in ServerObjects.ByServer.notifications:
        ServerObjects.ByServer.notifications[peer].put(message)


def sendFallbackMessage(socket, command=None):
    if command and HELP_LIST[command]:
        sendData(socket, f"Invalid command. Correct usage: {HELP_LIST[command]}")
    else:
        sendData(socket, "Invalid command. Type 'help' for available commands.")


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
        self.session = None
        self._stop_event = threading.Event()
        self.notificationHandler = NotificationHandler(conn, addr)
        self.lib = {
            'new': {
                'map': {
                    'function': self.add_map
                },
                'route': {
                    'function': self.add_route
                },
                'stop': {
                    'function': self.add_stop
                },
                'line': {
                    'function': self.add_line
                },
                'schedule': {
                    'function': self.add_schedule
                }
            },
            'list': {
                'map': {
                    'function': self.list_maps
                },
                'route': {
                    'function': self.list_routes
                },
                'schedule': {
                    'function': self.list_schedules
                },
                'line': {
                    'function': self.list_lines
                },
                'stop': {
                    'function': self.list_stops
                }
            },
            'open': {
                'map': {
                    'function': self.open_map
                }
            },
            'close': {
                'map': {
                    'function': self.close_map
                }
            }
        }

    def stop(self):
        self._stop_event.set()

    def open_map(self, data):
        payload = data['payload']
        mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
        mapIds = list(set(mapIds))
        if payload in mapIds:
            self.attachedSchedules = []
            self.selectedMapId = int(payload)
            for schedule in ServerObjects.ByServer.schedules:
                if schedule.map.id == self.selectedMapId:
                    self.attachedSchedules.append(schedule)
            index = mapIds.index(payload)
            self.selectedMap = ServerObjects.ByServer.maps[index]
            return f"Map with id {self.selectedMapId} is opened"

    def add_route(self, data):
        stopIds = data['stopIds'].split(' ')
        scheduleId = data['payload']
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(scheduleId)
        schedule_edited = self.attachedSchedules[index]
        stoplist = []
        for stopId in stopIds:
            stoplist.append(UUID(stopId))
        newRoute = Route(stoplist)
        schedule_edited.newroute(newRoute)
        #putNotification("New route is added.")
        return newRoute.get()

    def add_stop(self, data):
        direction = True if data['direction'] == '1' else False
        stopId = self.selectedMap.addstop(data['edgeId'], direction, float(data['percentage']), data['payload'])
        return str(stopId)

    def add_line(self, data):
        startTime = data['startTime'].split(':')
        endTime = data['endTime'].split(':')
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(data['scheduleId'])
        schedule_edited = self.attachedSchedules[index]
        addedLine = Line(datetime.time(hour=int(startTime[0]), minute=int(startTime[1])),
                         datetime.time(hour=int(endTime[0]), minute=int(endTime[1])),
                         datetime.time(minute=int(data['interval'])),
                         schedule_edited.getroute(int(data['routeId'])), data['payload'])
        schedule_edited.addLine(addedLine)
        #putNotification("New line is added.")
        print(addedLine.get())
        return addedLine.get()

    def add_schedule(self, data):  # takes no parameters?
        created_map = ServerObjects.ByServer.maps[0]
        schedule = Schedule(created_map)
        ServerObjects.ByServer.schedules.append(schedule)
        #putNotification(
        #    f"Thread {threading.get_ident()} added a new schedule on Map")
        return schedule.get()

    @staticmethod
    def list_maps(data):
        mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
        mapIds = list(set(mapIds))
        return mapIds

    def list_routes(self, data):
        payload = data['payload']
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(payload)
        schedule_edited = self.attachedSchedules[index]
        routes = schedule_edited.listroutes()
        return routes

    def list_schedules(self, data):
        return [schedule.get() for schedule in self.attachedSchedules]

    def list_lines(self, data):
        payload = data['payload']
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(payload)
        schedule_edited = self.attachedSchedules[index]
        return schedule_edited.listlines()

    def list_stops(self, data):
        return self.selectedMap.getStopsInfo()

    @staticmethod
    def add_map(data):
        payload = data['payload']
        ServerObjects.ByThread.mapLock.acquire()
        mapData = payload
        if mapData.startswith("{"):
            createdMap = Map(None, mapData)
        else:
            createdMap = Map(mapData)
        print('map get =', createdMap.get())
        ServerObjects.ByServer.maps.append(createdMap)
        ServerObjects.ByThread.mapLock.release()
        return createdMap.get()

    def close_map(self, data):
        self.selectedMap = None
        self.selectedMapId = 0
        return 'Map is closed'

    def check_session(self, data):
        if data['type'] == 'login':
            username = data['username']
            password = data['password']
            for user in ServerObjects.ByUser.users:
                if user.getUsername() == username and user.auth(password):
                    cookie = hashlib.sha256((username + password).encode('utf-8')).hexdigest()
                    self.session = cookie
                    sendData(self.conn, {
                        'result': 'success',
                        'username': username,
                        'cookie': cookie
                    })
                    return False
            sendData(self.conn, {'result': 'noSession'})
            return False
        if self.session == data['cookie']:
            return True
        sendData(self.conn, {'result': 'noSession'})
        return False

    def run(self):
        self.notificationHandler.start()
        print(f'Client {self.addr} is connected.')
        while not self._stop_event.is_set():
            try:
                data = getData(self.conn)
                print('data =', data, type(data))
                #sessionExits = self.check_session(data)
                #print('session exists?', sessionExits)
                #if not sessionExits:
                #    continue
                print('data in agent', data)
                # requestType = "ADD", "DELETE", "UPDATE", "NEW", "LOGIN"
                result = self.lib[data['type']][data['instance']]['function'](data)
                print('result =', result)
                sendData(self.conn, {'result': result})

                """
                if response[0] == ae.ADD_MAP:
                    
                if response[0] == ae.ADD_SCHEDULE:
                    ServerObjects.ByThread.addScheduleLock.acquire()
                    created_map = ServerObjects.ByServer.maps[0]
                    schedule = Schedule(created_map)
                    ServerObjects.ByServer.schedules.append(schedule)
                    putNotification(
                        f"Thread {threading.get_ident()} added a new schedule on Map")
                    ServerObjects.ByThread.addScheduleLock.release()
    
                if response[0] == ae.SHOW_ALL_THREADS:
                    json_data = json.dumps(ServerObjects.ByServer.addresses)
                    sendData(self.conn, json_data)
    
                if response[0] == ae.LIST_MAPS:
                    mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
                    mapIds = list(set(mapIds))
                    sendData(self.conn, f"{' '.join(mapIds)}")
    
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
                        sendData(self.conn, f"Map with id {self.selectedMapId} is opened\n")
    
                if response[0] == ae.CLOSE_MAP:
                    self.selectedMapId = 0
                    self.selectedMap = None
                    self.attachedSchedules = []
                    sendData(self.conn, f"Map is closed\n")
    
                if response[0] == ae.LIST_SCHEDULES:
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    schedIds = list(set(schedIds))
                    sendData(self.conn, ' '.join(schedIds))
    
                if response[0] == ae.LIST_STOPS:
                    stops = self.selectedMap.getStopsInfo()
                    sendData(self.conn, str(stops))
    
                if response[0] == ae.LIST_ROUTES:
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    routes = schedule_edited.listroutes()
                    sendData(self.conn, concat(routes))
    
                if response[0] == ae.ADD_ROUTE:
                    ServerObjects.ByThread.addRouteLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    stoplist = []
                    for i in range(int(response[2])):
                        stoplist.append(UUID(response[3 + i]))
                    schedule_edited.newroute(Route(stoplist))
                    putNotification("New route is added.")
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
                    putNotification(f"Route with id {route_edited} is updated.")
                    ServerObjects.ByThread.addRouteLock.release()
    
                if response[0] == ae.DEL_ROUTE:
                    ServerObjects.ByThread.addRouteLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    schedule_edited.delroute(int(response[2]))
                    putNotification(f"Route with id {int(response[2])} is deleted.")
                    ServerObjects.ByThread.addRouteLock.release()
    
                if response[0] == ae.LIST_LINES:
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    lines = schedule_edited.listlines()
                    sendData(self.conn, concat(lines))
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
                    putNotification("New line is added.")
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
                    putNotification(f"Line with id {line_edited} is updated.")
                    ServerObjects.ByThread.addLineLock.release()
    
                if response[0] == ae.DEL_LINE:
                    ServerObjects.ByThread.addLineLock.acquire()
                    schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
                    index = schedIds.index(response[1])
                    schedule_edited = self.attachedSchedules[index]
                    schedule_edited.delLine(int(response[2]))
                    putNotification(f"Line with id {int(response[2])} is deleted.")
                    ServerObjects.ByThread.addRouteLock.release()
            """
            except Exception as e:
                traceback.print_exc()
                sendData(self.conn, {'error': str(e)})
