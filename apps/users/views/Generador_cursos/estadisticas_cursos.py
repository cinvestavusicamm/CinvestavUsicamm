from django.shortcuts import render, redirect

def estadisticas_cursos(request):
    if request.session.get('usuario_rol') != 'Generador':
        return redirect('sesion')
    return render(request, 'Generador_cursos/estadisticas_de_cursos.html')