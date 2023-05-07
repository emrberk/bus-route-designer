import threading

from src.util import Utils
from src.server.ServerObjects import ServerObjects

class NotificationHandler(threading.Thread):
    def __init__(self, socket, peer):
        self.socket = socket
        self.peer = peer
        super().__init__()

    def run(self):
        while True:  # TODO: handle join with event
            message = ServerObjects.ByServer.notificationQueue.get()
            Utils.sendDataAsChunks(self.socket, message)
