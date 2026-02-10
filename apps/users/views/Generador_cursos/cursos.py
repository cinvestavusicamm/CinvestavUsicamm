from django.shortcuts import render, redirect

def cursos(request):
    if request.session.get('usuario_rol') != 'Generador':
        return redirect('sesion')
    return render(request, 'Generador_cursos/mis_cursos.html')