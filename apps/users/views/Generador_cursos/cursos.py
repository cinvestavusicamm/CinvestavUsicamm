from django.shortcuts import render, redirect

def cursos(request):
    if request.session.get('usuario_rol') != 'generador_cursos':
        return redirect('sesion')
    return render(request, 'Generador_cursos/mis_cursos.html')