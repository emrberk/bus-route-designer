import threading

from src.util import Utils

class Listener(threading.Thread):
    def __init__(self, s, killListener):
        self.socket = s
        self.killListener = killListener
        super().__init__()

    def run(self):
        while not self.killListener.is_set():
            message = Utils.getDataAsChunks(self.socket)
            # will handle based on notification type
            print('Notification from server:', message)

