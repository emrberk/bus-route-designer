import threading

from src.client.ClientObjects import ClientObjects
from src.util import Utils


class Sender(threading.Thread):
    def __init__(self, s, killSender):
        self.s = s
        self.killSender = killSender
        super().__init__()

    def run(self):
        while not self.killSender.is_set():
            message = ClientObjects.messageQueue.get()
            Utils.sendDataAsChunks(self.s, message)
