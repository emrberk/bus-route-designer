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


class Client(threading.Thread):
    def __init__(self, targetHost, targetPort):
        self.socket = None
        self.listener = None
        self.sender = None
        self.targetHost = targetHost
        self.targetPort = targetPort
        self.killListener = threading.Event()
        self.killSender = threading.Event()
        super().__init__()

        # Close opened ports when Ctrl-C pressed
        # signal.signal(signal.SIGINT, self.interruptHandler)
    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.targetHost, self.targetPort))
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
        self.socket.close()
        exit(1)
    """
