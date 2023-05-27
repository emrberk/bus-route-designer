import json

from django.shortcuts import render, redirect

from src.client.Client import Client
from src.client.ClientObjects import ClientObjects

try:
    client = Client('0.0.0.0', 2001)
    client.start()
except:
    client.join()
messageQueue = ClientObjects.incomingMessageQueue
responseQueue = ClientObjects.responseQueue


def index(request):
    if request.method == 'GET':
        if 'cookie' not in request.COOKIES:
            response = redirect('/api/login')
            return response
        return render(request, 'index.html')
    elif request.method == 'POST':
        data = dict(request.POST)
        for key in data:
            data[key] = data[key][0]
        data['cookie'] = request.COOKIES.get('cookie')
        messageQueue.put(json.dumps(data))
        print('put data ', json.dumps(data))
        responseMessage = responseQueue.get()
        print('get data ', responseMessage)
        # if responseMessage['result'] == 'noSession':
        #    return redirect('/api/login')
        return render(request, 'index.html', {'result': json.dumps(responseMessage).replace("'", '"')})


def simulator(request):
    if request.method == 'POST':
        data = {
            'speed': request.POST['speed'],
            'startTime': request.POST['startTime'],
            'type': 'simulation'
        }
        messageQueue.put(json.dumps(data))
        ClientObjects.simulationData = []
        return redirect('/api/simulator')
        # return render(request, 'simulator.html', {'result': 'Simulation started'})
    else:
        return render(request, 'simulator.html', {'count': str(len(ClientObjects.simulationData)),
                                                  'result': json.dumps(ClientObjects.simulationData).replace("'", '"')})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        info = {
            'username': username,
            'password': password,
            'type': 'login'
        }
        messageQueue.put(json.dumps(info))
        responseMessage = responseQueue.get()
        if responseMessage['result'] == 'noSession':
            return render(request, 'login.html', {'errorMessage': 'User not found'})
        response = redirect('/api/')
        response.set_cookie(key='cookie', value=responseMessage['cookie'])
        return response
    return render(request, 'login.html')
