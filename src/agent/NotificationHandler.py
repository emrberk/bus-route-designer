import json
import threading

from src.server.ServerObjects import ServerObjects


class NotificationHandler(threading.Thread):
    def __init__(self, websocket, peer):
        self.websocket = websocket
        self.peer = peer
        super().__init__()

    def run(self):
        while True:  # TODO: handle join with event
            message = ServerObjects.ByServer.notifications[self.peer].get()
            print("message in notHandler: ", message)
            self.websocket.send(json.dumps(message))
