import argparse
import socket
import threading
import sys
import signal
sys.path.append('../../')

from src.client.NotificationListener import NotificationListener
from src.client.Sender import Sender
from src.client.ClientObjects import ClientObjects


class Client:
    def __init__(self):
        self.listenerSocket = None
        self.senderSocket = None
        self.listener = None
        self.sender = None
        self.killListener = threading.Event()
        self.killSender = threading.Event()

        # Close opened ports when Ctrl-C pressed
        signal.signal(signal.SIGINT, self.interruptHandler)

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-th', '--targetHost', help="Target host address", type=str, required=True
        )
        parser.add_argument(
            '-tp', '--targetPort', help="Target port number", type=int, required=True
        )
        parser.add_argument(
            '-sp', '--selfPort', help="Self port number to listen notifications", type=int, required=True
        )
        self.args = parser.parse_args()

        try:
            senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            senderSocket.connect((self.args.targetHost, self.args.targetPort))
            self.senderSocket = senderSocket
            # introduce the listener socket of client to server
            senderSocket.send(f'{self.args.selfPort}'.encode())
            sender = Sender(senderSocket, self.killSender)
            self.sender = sender
            sender.start()
            print(self.args)
            listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listenerSocket.bind(('0.0.0.0', self.args.selfPort))
            self.listenerSocket = listenerSocket
            listener = NotificationListener(listenerSocket, self.args.selfPort, self.killListener)
            self.listener = listener
            listener.start()

            userInput = input()
            ClientObjects.messageQueue.put(userInput)


        except:
            self.killListener.set()
            self.killSender.set()
            self.listener.join()
            self.sender.join()
            raise ConnectionError()

    def interruptHandler(self, signum, frame):
        self.killSender.set()
        self.killListener.set()
        self.senderSocket.close()
        self.listenerSocket.close()
        exit(1)

if __name__ == "__main__":
    client = Client()
