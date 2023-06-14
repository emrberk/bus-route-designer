import asyncio
import threading

from src.client.ClientObjects import ClientObjects


class Sender(threading.Thread):
    def __init__(self, websocket, killSender):
        self.websocket = websocket
        self.killSender = killSender
        super().__init__()

    async def send_message(self, message):
        await self.websocket.send(message)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while not self.killSender.is_set():
            message = ClientObjects.messageQueue.get()
            loop.run_until_complete(self.send_message(message))

        loop.close()
