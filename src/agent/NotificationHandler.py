import threading

from src.server.ServerObjects import ServerObjects
from src.util.Utils import *


class NotificationHandler(threading.Thread):
    def __init__(self, socket, peer):
        self.socket = socket
        self.peer = peer
        super().__init__()

    def run(self):
        while True:  # TODO: handle join with event
            message = ServerObjects.ByServer.notifications[self.peer].get()
            sendData(self.socket, message)
