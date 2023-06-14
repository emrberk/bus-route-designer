import asyncio
import sys
import threading

import websockets

sys.path.append('../../')

from src.util import Utils
from src.client.Listener import Listener
from src.client.Sender import Sender
from src.client.ClientObjects import ClientObjects


class Client(threading.Thread):
    def __init__(self, targetHost, targetPort):
        self.websocket = None
        self.listener = None
        self.sender = None
        self.targetHost = targetHost
        self.targetPort = targetPort
        self.killListener = threading.Event()
        self.killSender = threading.Event()
        super().__init__()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    async def connect(self):
        try:
            uri = f"ws://{self.targetHost}:{self.targetPort}"
            self.websocket = await websockets.connect(uri)

            sender = Sender(self.websocket, self.killSender)
            self.sender = sender
            sender.start()

            listener = Listener(self.websocket, self.killListener)
            self.listener = listener
            listener.start()

        except:
            self.killListener.set()
            self.killSender.set()
            self.listener.join()
            self.sender.join()
            raise ConnectionError()

        while True:
            try:
                userInput = ClientObjects.incomingMessageQueue.get()
                packets = Utils.divideIntoPackets(userInput)
                for packet in packets:
                    ClientObjects.messageQueue.put(packet)
            except:
                pass

    """
    def interruptHandler(self, signum, frame):
        self.killSender.set()
        self.killListener.set()
        self.websocket.close()
        exit(1)
    """
