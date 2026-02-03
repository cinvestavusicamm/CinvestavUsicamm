from django.shortcuts import render, redirect

def chat(request):
    if request.session.get('usuario_rol') != 'evaluador':
        return redirect('sesion') 
    return render(request, 'evaluador/chat_ia.html')