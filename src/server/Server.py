import argparse
import asyncio
import queue
import signal
import sys

import websockets

sys.path.append('../../')
from src.agent.Agent import Agent
from src.server.ServerObjects import ServerObjects


class Server:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', help='Websocket server port number', type=int, required=True)
        self.messageQueue = queue.Queue()
        self.args = parser.parse_args()
        self.addScheduleLock = asyncio.Lock()
        self.server = None

        # Close opened ports when Ctrl-C pressed
        signal.signal(signal.SIGINT, self.interruptHandler)

    async def startServer(self, websocket, path):
        addr = websocket.remote_address
        ServerObjects.ByServer.addresses.append(addr)
        ServerObjects.ByServer.notifications[addr] = queue.Queue()
        newThread = Agent(websocket, addr)
        ServerObjects.ByServer.threads.append(newThread)
        newThread.start()
        await newThread.run()

    def interruptHandler(self, signum, frame):
        if self.server:
            self.server.close()
            asyncio.get_event_loop().run_until_complete(self.server.wait_closed())
        exit(1)

    def run(self):
        print(f'Websocket server is listening on port {self.args.port}...')

        self.server = websockets.serve(self.startServer, 'localhost', self.args.port)

        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    server = Server()
    server.run()
