import datetime
import json
import math

import numpy as np

from src.Point import Point


def euclideanDistance(p1: Point, p2: Point) -> float:
    # to find real distance in km
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) * 16.8 / 1000


def dot(p0: Point, p1: Point) -> float:
    return float(np.dot(tuple(p0), tuple(p1)))


def calculateD(p0: Point, p1: Point, p2: Point) -> float:
    return dot(p0 - p1, p2 - p1) / dot(p2 - p1, p2 - p1)


def calculateS(p1: Point, p2: Point, d: float) -> Point:
    return p1 + (p2 - p1) * d


def calculateDistance(p1: Point, p2: Point, location: Point) -> list:
    d = calculateD(location, p1, p2)
    point = (-1, -1)
    if d <= 0:
        point = p1
    elif d >= 1:
        point = p2
    else:
        point = calculateS(p1, p2, d)

    distance = euclideanDistance(location, point)
    return [point, distance]


def add_times(time1, time2):
    t1 = datetime.datetime.strptime(str(time1), '%H:%M:%S')
    t2 = datetime.datetime.strptime(str(time2), '%H:%M:%S')
    total = t1 + (t2 - datetime.datetime(1900, 1, 1))
    return datetime.time(total.hour, total.minute, total.second)


def time_difference(start, end):
    if end < start:
        end += datetime.timedelta(days=1)
    diff = datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(),
                                                                                             start)
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return datetime.time(hours, minutes, seconds)


def getTimeStr(time):
    return time.strftime("%H:%M")


def minToTime(mins):
    time = datetime.timedelta(minutes=mins)
    hour = int(time.seconds / 3600)
    minute = int((time.seconds % 3600) / 60)
    second = time.seconds % 60
    return "{:02d}:{:02d}:{:02d}".format(hour, minute, second)


def read_json_input():
    while True:
        try:
            path = input("Enter the path of Json: ")
            file = open(path)
            data = json.load(file)
            file.close()
            return data
        except ValueError:
            print("Invalid JSON object. Try again.")


def parse_json_input(path):
    try:
        file = open(path)
        data = json.load(file)
        file.close()
        return data
    except ValueError:
        print("Invalid JSON object. Try again.")


def compare_str(strs, str2):
    for str1 in strs:
        length = len(str1)
        if len(str2) >= length:
            if str1 == str2[:length]:
                return [True, length]
    return [False]


def divideIntoPackets(message):
    message = message.replace('\n', '').replace('\r', '')
    encodedMessage = message.encode()
    numChunks = math.ceil(len(encodedMessage) / 1024)
    chunks = []
    for i in range(numChunks):
        if len(encodedMessage) >= 1024:
            chunks.append(encodedMessage[:1024])
            encodedMessage = encodedMessage[1024:]
        else:
            chunks.append(encodedMessage)
    if len(chunks) > 1:
        length = f"S-{len(chunks)}"
        extraCharacters = 1024 - len(length)
        length += extraCharacters * chr(0)
        chunks = [length.encode()] + chunks
    return chunks


def sendData(s, data):
    chunks = divideIntoPackets(json.dumps(data))
    for chunk in chunks:
        s.send(chunk)


async def receive(websocket):
    print("bunu bekliyom kanka: receive")
    data = await websocket.recv()
    try:
        json_data = json.loads(data)
        return json_data
    except json.JSONDecodeError:
        print("Error: Invalid JSON data")
        return None


def getData(s):
    data = s.recv(1024).decode().replace('\n', '').replace('\r', '')
    if data.startswith("S-"):
        end = data.index(chr(0))
        print('end =', end)
        numPackets = int(data[2:end])
        print(numPackets)
    else:
        return json.loads(data.replace('\r\n', ''))
    receivedPackets = []
    while len(receivedPackets) < numPackets:
        packet = s.recv(1024)
        receivedPackets.append(packet)
    receivedPackets = b''.join(receivedPackets)
    return json.loads(receivedPackets.decode().replace('\r\n', ''))


def concat(list):
    string = ""
    if type(list) == str:
        return list
    for i in range(len(list)):
        string += str(list[i])
        string += "\n"
    return string
