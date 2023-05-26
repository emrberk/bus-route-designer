from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from src.client.Client import Client
from src.client.ClientObjects import ClientObjects
import json

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
        responseMessage = responseQueue.get()
        #if responseMessage['result'] == 'noSession':
        #    return redirect('/api/login')
        return render(request, 'index.html', {'result': responseMessage})

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
