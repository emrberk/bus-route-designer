import asyncio
import threading

from src.client.ClientObjects import ClientObjects
from src.util import Utils


class Listener(threading.Thread):
    def __init__(self, websocket, killListener):
        self.websocket = websocket
        self.killListener = killListener
        super().__init__()

    async def receive_data(self):
        message = await Utils.receive(self.websocket)
        print("message:", message)
        # Bildirim türüne göre işleme alınacak
        if 'type' in message and message['type'] == 'simulation':
            ClientObjects.simulationData.append(message['data'])
        else:
            ClientObjects.responseQueue.put(message)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while not self.killListener.is_set():
            loop.run_until_complete(self.receive_data())
