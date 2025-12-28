from django.shortcuts import render

def index(request):
    return render(request, 'users/index.html')

def login(request):
    return render(request, 'users/sesion.html')

def registro(request):
    return render(request, 'users/registro.html')

def dashboard(request):
    return render(request, 'users/dash.html')

def panel_admin(request):
    return render(request, 'users/paneladm.html')

def chat(request):
    return render(request, 'users/chat.html')

def prueba(request):
    return render(request, 'users/prueba.html')
