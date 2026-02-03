from django.shortcuts import render, redirect

def index_generador(request):
    if request.session.get('usuario_rol') != 'generador_cursos':
        return redirect('sesion')
    return render(request, 'Generador_cursos/index_generador_de_cursos.html')