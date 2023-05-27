from queue import Queue


class ClientObjects:
    messageQueue = Queue()
    incomingMessageQueue = Queue()
    responseQueue = Queue()
    simulationData = []

