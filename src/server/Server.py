import argparse
import queue
import socket
import threading
import sys
import signal
sys.path.append('../../')
from src.agent.Agent import Agent
from src.server.ServerObjects import ServerObjects


class Server:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', help='TCP server port number', type=int, required=True)
        self.messageQueue = queue.Queue()
        self.args = parser.parse_args()
        self.addScheduleLock = threading.Lock()
        self.s = None

        # Close opened ports when Ctrl-C pressed
        signal.signal(signal.SIGINT, self.interruptHandler)

    """
    def printMessages(self):
        while True:
            if not self.messageQueue.empty():
                print(self.messageQueue.queue[0])
                if all(thread.newMessage.is_set() for thread in ServerObjects.ByServer.threads):
                    all(thread.newMessage.clear() for thread in ServerObjects.ByServer.threads)
                    self.messageQueue.get()
                    break
            else:
                break
    """

    def startServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.args.port))
            self.s = s
            s.listen()

            print(f'TCP server is listening on port {self.args.port}...')

            while True:
                conn, addr = s.accept()
                ServerObjects.ByServer.addresses.append(addr)
                ServerObjects.ByServer.notifications[addr] = queue.Queue()
                newThread = Agent(conn, addr)
                ServerObjects.ByServer.threads.append(newThread)
                newThread.start()

    def interruptHandler(self, signum, frame):
        self.s.close()
        exit(1)


if __name__ == '__main__':
    server = Server()
    server.startServer()
