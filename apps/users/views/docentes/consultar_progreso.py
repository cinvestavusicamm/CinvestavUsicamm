from django.shortcuts import render, redirect

def consultar_progreso(request):
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('sesion')
    return render(request, 'Consulta_progreso.html')