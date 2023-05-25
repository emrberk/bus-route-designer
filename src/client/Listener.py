import threading

from src.util import Utils
from src.client.ClientObjects import ClientObjects

class Listener(threading.Thread):
    def __init__(self, s, killListener):
        self.socket = s
        self.killListener = killListener
        super().__init__()

    def run(self):
        while not self.killListener.is_set():
            message = Utils.getData(self.socket)
            # will handle based on notification type
            ClientObjects.responseQueue.put(message)

