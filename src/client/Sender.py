import threading
import math

from src.client.ClientObjects import ClientObjects


class Sender(threading.Thread):
    def __init__(self, s, killSender):
        self.s = s
        self.killSender = killSender
        super().__init__()

    def run(self):
        while not self.killSender.is_set():
            result = self.s.recv(1024)
            print('Sender received result ', result.decode())
            message = ClientObjects.messageQueue.get()
            message = message.encode()
            numChunks = math.ceil(len(message) // 1024)
            chunks = []
            for i in range(numChunks):
                if len(message) >= 1024:
                    chunks.append(message[:1024])
                    message = message[1024:]
                else:
                    chunks.append(message)

            self.s.send(f'{numChunks}'.encode())
            for chunk in chunks:
                self.s.send(chunk)


            # do something with the result...
        self.s.close()
