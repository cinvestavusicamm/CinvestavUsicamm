from django.shortcuts import render, redirect

def validaciones(request):
    if request.session.get('usuario_rol') != 'Evaluador':
        return redirect('sesion') 
    return render(request, 'evaluador/validaciones.html')