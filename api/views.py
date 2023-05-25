from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from src.client.Client import Client
from src.client.ClientObjects import ClientObjects
import json


print('before client')
client = Client('0.0.0.0', 2000)
client.start()
print('after client')
messageQueue = ClientObjects.incomingMessageQueue
responseQueue = ClientObjects.responseQueue


def index(request):
    if request.method == 'GET':
        if 'cookie' not in request.COOKIES:
            response = redirect('/api/login')
            return response
        return render(request, 'index.html')
    elif request.method == 'POST':
        type = request.POST.get('type')
        instance = request.POST.get('instance')
        payload = request.POST.get('payload')
        cookie = request.COOKIES.get('cookie')
        messageQueue.put(json.dumps({'type': type, 'instance': instance, 'payload': payload, 'cookie': cookie}))
        responseMessage = responseQueue.get()
        return render(request, 'index.html', {'result': responseMessage})
        if responseMessage['result'] == 'noSession':
            return redirect('/api/login')
        return

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
