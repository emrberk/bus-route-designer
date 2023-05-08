import argparse
import socket
import threading
import sys
import signal
import json
sys.path.append('../../')

from src.util import Utils
from src.client.Listener import Listener
from src.client.Sender import Sender
from src.client.ClientObjects import ClientObjects


class Client:
    def __init__(self):
        self.socket = None
        self.listener = None
        self.sender = None
        self.killListener = threading.Event()
        self.killSender = threading.Event()

        # Close opened ports when Ctrl-C pressed
        signal.signal(signal.SIGINT, self.interruptHandler)

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-H', '--host', help="Target host address", type=str, required=True
        )
        parser.add_argument(
            '-p', '--port', help="Target port number", type=int, required=True
        )
        self.args = parser.parse_args()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.args.host, self.args.port))
            self.socket = s
            # introduce the listener socket of client to server
            sender = Sender(self.socket, self.killSender)
            self.sender = sender
            sender.start()
            listener = Listener(self.socket, self.killListener)
            self.listener = listener
            listener.start()

        except:
            self.killListener.set()
            self.killSender.set()
            self.listener.join()
            self.sender.join()
            raise ConnectionError()

        while True:
            userInput = input()
            if userInput == 'new':
                filePath = userInput[3:]
                file = open(filePath)
                jsonFile = json.load(file)
                userInput = f"new {json.dumps(jsonFile)}"
            packets = Utils.divideIntoPackets(userInput)
            for packet in packets:
                ClientObjects.messageQueue.put(packet)

    def interruptHandler(self, signum, frame):
        self.killSender.set()
        self.killListener.set()
        self.socket.close()
        exit(1)


if __name__ == "__main__":
    client = Client()
