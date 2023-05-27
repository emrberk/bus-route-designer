"""
                if response[0] == ae.ADD_MAP:
                    ServerObjects.ByThread.addMapLock.acquire()
                    mapData = ' '.join(response[1:])
                    if mapData.startswith("{"):
                        createdMap = Map(None, mapData)
                    else:
                        createdMap = Map(mapData)
                    ServerObjects.ByServer.maps.append(createdMap)
                    putNotification(
                        f"Thread {threading.get_ident()} added a new Map")
                    ServerObjects.ByThread.addMapLock.release()
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
