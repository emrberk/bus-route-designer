import cmd
import datetime
from uuid import UUID

from src.Line import Line
from src.Map import Map
from src.Route import Route
from src.Schedule import Schedule
from src.user.User import User


class DemoApp(cmd.Cmd):
    intro = "Welcome to the DemoAPP for Bus Route Designer. Type help or ? to list commands.\n"
    prompt = '(Schedule) '
    file = None

    def __init__(self):
        self.defaultMap = Map()
        self.token = ""
        self.schedule = Schedule(self.defaultMap)
        super().__init__()

    def do_demo(self, args):
        """It can be useful for adding default data"""
        user = User("def", "def@gmail.com", "default account", "1234")
        token = user.login("1234")
        User.users.append(user)
        self.token = token
        s1 = self.defaultMap.addstop('1', True, 100, 't1')
        s2 = self.defaultMap.addstop('2', True, 100, 't2')
        s3 = self.defaultMap.addstop('3', True, 100, 't3')
        self.schedule.newroute([Route([s1, s2, s3])])
        self.schedule.addLine(Line(datetime.time(hour=14, minute=30), datetime.time(hour=20), datetime.time(minute=30),
                                   self.schedule.getroute(1), "ilk line"))

    def tokenize(self):
        if self.token == "":
            print("To use this functionality, you should be logged in.")
            return False
        else:
            return True

    @staticmethod
    def do_signUp(arg):
        """Create a new account"""
        user = User.createUser()

    @staticmethod
    def do_listUsers(arg):
        """List all the users in BRD ecosystem"""
        User.listUsers()

    def do_login(self, arg):
        """login to site : email - password authentication"""
        print("Username : ")
        username = input()
        user = User.getUser(username)
        if user is not None:
            print("Password : ")
            psswd = input()
            token = user.login(psswd)
            self.token = token

    def do_logout(self, arg):
        """logout from site"""
        if self.token == "":
            print("You are not logged in.")
        else:
            print("you are logged out.")
            self.token = ""

    def do_openMap(self, map):
        """load a map or use default one"""
        # TODO: düzeltilecek
        if self.tokenize():
            self.defaultMap = map
            self.schedule = Schedule(self.defaultMap)

    def do_addStop(self, arg):
        "Add a new stop on the map"
        edge_id = input("Enter the edge ID: ")
        direction = input("Enter the direction (True or False): ")
        percentage = float(input("Enter the percentage: "))
        description = input("Enter the description: ")

        stop_id = self.defaultMap.addstop(edge_id, direction, percentage, description)
        print(f"Stop added with ID: {stop_id}")

    def do_delStop(self, arg):
        """Delete a stop from the map"""
        if self.tokenize():
            stop_id = input("Enter the stop ID: ")
            try:
                stop = self.defaultMap.getStop(UUID(stop_id))
                id = stop.get("id")
                self.defaultMap.delStop(id)
                print(f" Stop {id} is deleted successfully.")
            except Exception as e:
                print("An error happened : ", e)

    def do_getStop(self, arg):
        """get basic information about a stop"""
        if self.tokenize():
            stop_id = input("Enter the stop ID: ")
            try:
                print(self.defaultMap.getStop(UUID(stop_id)))
            except Exception as e:
                print("An error happened : ", e)

    def do_stopDistance(self, args):
        """finds and returns the distance between two stops."""
        if self.tokenize():
            stopID1 = input("Enter the stop ID for first stop: ")
            stopID2 = input("Enter the stop ID for first stop: ")
            try:
                self.defaultMap.stopdistance(UUID(stopID1), UUID(stopID2))
            except Exception as e:
                print(f"There is no stop with id : {stopID2}")
            finally:
                pass

    def do_shortestStop(self, arg):
        """Gives the closest stop from given location."""
        # TODO: bura hata atıyor düzeltilecek
        if self.tokenize():
            x = float(input("Enter the x coordinate: "))
            y = float(input("Enter the y coordinate: "))
            location = {"x": x, "y": y}
            try:
                stop_id = self.defaultMap.shorteststop(location)
                print(self.defaultMap.getStop(UUID(stop_id)))
            except Exception as e:
                print("An error happened : ", e)

    def do_showStops(self, arg):
        """List all the stops in the map"""
        if self.tokenize():
            self.defaultMap.getStopsInfo()

    def do_closestEdge(self, arg):
        if self.tokenize():
            x = float(input("Enter the x coordinate: "))
            y = float(input("Enter the y coordinate: "))
            location = {"x": x, "y": y}
            try:
                print(self.defaultMap.closestedge(location))
            except Exception as e:
                print("An error happened : ", e)

    def do_newRoute(self, arg):
        """
        Creates a new route with given stop ids
        Usage: createRoute <stop_id1> <stop_id2> ...
        """
        if self.tokenize():
            stop_ids = arg.split()
            for i in range(0, len(stop_ids)):
                stop_ids[i] = UUID(stop_ids[i])
            if len(stop_ids) == 0:
                print("Please provide at least one stop id")
                return
            route = Route(stop_ids)
            self.schedule.newroute([route])
            print(f"Route created with id: {route.id}")

    def do_getRoute(self, arg):
        """
        Gets route with given id
        Usage: getRoute <route_id>
        """
        if self.tokenize():
            routeId = int(arg)
            try:
                print(self.schedule.getroute(routeId))
            except Exception as e:
                print("An error happened :", e)

    def do_updateRoute(self, arg):
        """
        updates the route with given stop ids
        Usage: updateRoute <route_id> <stop_id1> <stop_id2> ...
        """
        if self.tokenize():
            stop_ids = arg.split()
            if len(stop_ids) == 1:
                print("Please provide at least one stop id")
                return
            id = int(stop_ids[0])
            for i in range(1, len(stop_ids)):
                stop_ids[i] = UUID(stop_ids[i])
            self.schedule.updateroute(id, stop_ids[1:])
            print(f"Route updated with id: {id}")

    def do_delRoute(self, arg):
        """
        Deletes the routes with given ids
        Usage: createRoute <route_id1> <route_id2> <route_id2> ...
        """
        if self.tokenize():
            route_ids = arg.split()
            if len(route_ids) == 0:
                print("Please provide at least one route id")
                return
            for i in range(0, len(route_ids)):
                route_ids[i] = int(route_ids[i])
            for id in route_ids:
                self.schedule.delroute(id)
                print(f"Route deleted with id: {id}")

    def do_showRoutes(self, arg):
        """lists all the routes in Schedule"""
        if not self.schedule.routes:
            print("There is no Routes in the schedule now.")
        for route in self.schedule.routes:
            print(route)

    def do_showLines(self, arg):
        """lists all the lines in Schedule."""
        if not self.schedule.lines:
            print("There is no Line in the schedule now.")
        for line in self.schedule.lines:
            print(line)

    def do_newLine(self, arg):
        """Creates a new Line in the Schedule."""
        if self.tokenize():
            while True:
                start_time_str = input("Enter start time in HH:MM format: ")
                try:
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                end_time_str = input("Enter end time in HH:MM format: ")
                try:
                    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                rep_time_str = input("Enter repetition time in Minutes: ")
                try:
                    rep_time = datetime.datetime.strptime(rep_time_str, "%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in Minutes.")
                    continue

                route_str = input("Enter a route id: ")
                try:
                    route_id = int(route_str)
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                description = input("Enter description (optional): ")

                newLine = Line(start_time, end_time, rep_time, self.schedule.getroute(route_id), description)
                self.schedule.lines.append(newLine)
                print("New line is created")
                break

    def do_updateLine(self, arg):
        """
        Updates the given Line in the Schedule.
        Usage : updateLine <line_id>
        """
        line_id = arg.split()
        if len(line_id) == 0:
            print("Please provide at least one line id")
            return
        id = int(line_id[0])
        if self.tokenize():
            while True:
                start_time_str = input("Enter start time in HH:MM format: ")
                try:
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                end_time_str = input("Enter end time in HH:MM format: ")
                try:
                    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                rep_time_str = input("Enter repetition time in Minutes: ")
                try:
                    rep_time = datetime.datetime.strptime(rep_time_str, "%M").time()
                except ValueError:
                    print("Invalid format! Please enter time in Minutes.")
                    continue

                route_str = input("Enter a route id: ")
                try:
                    route_id = int(route_str)
                except ValueError:
                    print("Invalid format! Please enter time in HH:MM format.")
                    continue

                description = input("Enter description (optional): ")

                self.schedule.updateLine(id, start_time, end_time, rep_time, self.schedule.getroute(route_id),
                                         description)
                print("Given line is updated")
                break

    def do_delLine(self, arg):
        """
        Updates the given Line in the Schedule.
        Usage : updateLine <line_id>
        """
        line_id = arg.split()
        if len(line_id) == 0:
            print("Please provide at least one line id")
            return
        id = int(line_id[0])
        if self.tokenize():
            self.schedule.delLine(id)

    def do_lineInfo(self, arg):
        """
        Gives detailed line information
        Usage : lineInfo <line_id>
        """
        if self.tokenize():
            line_ids = arg.split()
            if len(line_ids) == 0:
                print("Please provide one route id")
                return
            line_ids[0] = int(line_ids[0])
            self.schedule.lineinfo(line_ids[0])

    def do_stopInfo(self, arg):
        """
        Gives detailed line information
        Usage : stopInfo <stop_id>
        """
        if self.tokenize():
            stop_ids = arg.split()
            if len(stop_ids) == 0:
                print("Please provide one route id")
                return
            stop_ids[0] = UUID(stop_ids[0])
            self.schedule.stopinfo(stop_ids[0])

    @staticmethod
    def do_exit(arg):
        exit(0)


if __name__ == '__main__':
    demoApp = DemoApp()
    demoApp.cmdloop()
