import threading

from src.client.ClientObjects import ClientObjects
from src.util import Utils


class Sender(threading.Thread):
    def __init__(self, socket, killSender):
        self.socket = socket
        self.killSender = killSender
        super().__init__()

    def run(self):
        while not self.killSender.is_set():
            message = ClientObjects.messageQueue.get()
            self.socket.send(message)
