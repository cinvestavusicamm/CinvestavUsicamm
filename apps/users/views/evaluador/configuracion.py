from django.shortcuts import render, redirect

def configuracion(request):
    if request.session.get('usuario_rol') != 'Evaluador':
        return redirect('sesion') 
    return render(request, 'evaluador/configuracion.html')