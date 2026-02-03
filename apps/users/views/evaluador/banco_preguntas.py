from django.shortcuts import render, redirect

def banco_preguntas(request):
    if request.session.get('usuario_rol') != 'evaluador':
        return redirect('sesion') 
    return render(request, 'evaluador/banco_preguntas.html')