import hashlib
import queue
import threading
import traceback
from uuid import UUID

from src.Line import Line
from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.agent.HelpCommand import HELP_LIST
from src.agent.NotificationHandler import NotificationHandler
from src.server.ServerObjects import ServerObjects
from src.simulator.Simulator import Simulator
from src.util.Utils import *


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
        self.simulator = None
        self.stop_simulation = threading.Event()
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
            },
            'delete': {
                'map': {
                    'function': self.delete_map
                },
                'route': {
                    'function': self.delete_route
                },
                'schedule': {
                    'function': self.delete_schedule
                },
                'line': {
                    'function': self.delete_line
                },
                'stop': {
                    'function': self.delete_stop
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
        # putNotification("New route is added.")
        return newRoute.get()

    def delete_route(self, data):
        print("mydata: ", data)
        routeId = data['deleteRoute']
        scheduleId = data['payload']
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(scheduleId)
        schedule_edited = self.attachedSchedules[index]
        schedule_edited.delroute(int(routeId))
        return f"route with id {routeId} is deleted"

    @staticmethod
    def delete_schedule(data):
        payload = data['payload']
        scheduleIds = [str(schedule.id) for schedule in ServerObjects.ByServer.schedules]
        index = scheduleIds.index(payload)
        del ServerObjects.ByServer.schedules[index]
        return f"Schedule with id {payload} is deleted"

    def delete_line(self, data):
        scheduleId = data['payload']
        lineId = data['lineId']
        schedIds = [str(schedule.id) for schedule in self.attachedSchedules]
        index = schedIds.index(scheduleId)
        schedule_edited = self.attachedSchedules[index]
        schedule_edited.delLine(int(lineId))
        return f"Line with id {int(lineId)} is deleted."

    def delete_stop(self, data):
        payload = data['payload']
        self.selectedMap.delStop(UUID(payload))
        return f"stop with id {payload} is deleted"

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
        addedLine = Line(datetime.time(hour=int(startTime[0]), minute=int(startTime[1]), second=0),
                         datetime.time(hour=int(endTime[0]), minute=int(endTime[1]), second=0),
                         datetime.timedelta(minutes=int(data['interval'])),
                         schedule_edited.getroute(int(data['routeId'])), data['payload'])
        schedule_edited.addLine(addedLine)
        ServerObjects.ByServer.lines.append(addedLine)
        # putNotification("New line is added.")
        return addedLine.get()

    def add_schedule(self, data):  # takes no parameters?
        created_map = ServerObjects.ByServer.maps[0]
        schedule = Schedule(created_map)
        ServerObjects.ByServer.schedules.append(schedule)
        # putNotification(
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

    def delete_map(self, data):
        payload = data['payload']
        if self.selectedMapId == int(payload):
            self.selectedMap = None
            self.selectedMapId = 0
        mapIds = [str(maps.id) for maps in ServerObjects.ByServer.maps]
        mapIds = list(set(mapIds))
        index = mapIds.index(payload)
        del ServerObjects.ByServer.maps[index]
        return f"map with id {payload} is deleted."

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
                # sessionExits = self.check_session(data)
                # print('session exists?', sessionExits)
                # if not sessionExits:
                #    continue
                if data['type'] == 'simulation':
                    if self.simulator:
                        continue
                    startTime = data['startTime'].split(':')
                    self.simulator = Simulator(
                        self.selectedMap,
                        ServerObjects.ByServer.lines,
                        ServerObjects.ByServer.notifications,
                        int(data['speed']),
                        datetime.time(hour=int(startTime[0]), minute=int(startTime[1])),
                        putNotification,
                        self.stop_simulation
                    )
                    self.simulator.start()
                else:
                    if self.simulator:
                        self.stop_simulation.set()
                        self.simulator.join()
                    result = self.lib[data['type']][data['instance']]['function'](data)
                    print('result =', result)
                    sendData(self.conn, {'result': result})

            except Exception as e:
                traceback.print_exc()
                sendData(self.conn, {'error': str(e)})
