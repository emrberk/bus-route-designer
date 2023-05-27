from src.Map import Map
from typing import List, Dict, Tuple
from src.Line import Line
import queue
import datetime
import time
import threading


class Simulator(threading.Thread):
    def __init__(self, map: Map,
                 lines: List[Line],
                 notifications: Dict[Tuple, queue.Queue],
                 speedFactor: int,
                 startTime: datetime.time,
                 putNotification,
                 stopSimulation
                 ):
        self.map = map
        self.lines = lines
        self.notifications = notifications
        self.simulationData = {}
        # 1 second in real time corresponds to {speedFactor} seconds in simulation
        self.speedFactor = speedFactor
        self.startTime = startTime
        self.putNotification = putNotification
        self.stopSimulation = stopSimulation
        # Create precomputed simulation data of all lines
        for line in self.lines:
            simulationData = line.createDailySimulationData(map)
            for data in simulationData:
                print(data, type(data))
                # if there is a data belongs to this time already
                if data in self.simulationData:
                    self.simulationData[data].append(simulationData[data])
                # create new list belongs to this time
                else:
                    self.simulationData[data] = [simulationData[data]]
        # Sort the data wrt times
        times = list(self.simulationData.keys())
        times.sort()
        sortedData = {}
        for time in times:
            if time > startTime.strftime("%H:%M:%S"):
                sortedData[time] = self.simulationData[time]
        self.simulationData = sortedData
        super().__init__()

    def run(self):
        # Start with current time, sleep until the next event in simulationData
        # put the event as a notification, repeat until no events left.
        currentTime = self.startTime
        keys = list(self.simulationData.keys())
        while not self.stopSimulation.is_set() and len(keys) > 0:
            nextEventTime = datetime.datetime.strptime(keys[0], "%H:%M:%S").time()
            dummy = datetime.date(1, 1, 1)
            nextEventTime1 = datetime.datetime.combine(dummy, nextEventTime)
            currentTime1 = datetime.datetime.combine(dummy, currentTime)
            sleepTimeInSec = (nextEventTime1 - currentTime1).total_seconds() / self.speedFactor
            time.sleep(sleepTimeInSec)
            print('i will put ', self.simulationData[keys[0]])
            self.putNotification({'type': 'simulation', 'data': self.simulationData[keys[0]]})
            keys = keys[1:]
            currentTime = nextEventTime
