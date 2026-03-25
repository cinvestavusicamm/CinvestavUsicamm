from django.shortcuts import render, redirect
from ..models import Institucion, Usuario, Rol
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def dashboard(request):
    if not request.session.get('usuario_id'):
        return redirect('sesion')

    return render(request, 'bienvenida.html', {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
    })

