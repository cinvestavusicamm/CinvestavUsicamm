from django.shortcuts import render, redirect

def index_generador(request):
    if request.session.get('usuario_rol') != 'Generador':
        return redirect('sesion')
    return render(request, 'Generador_cursos/index_generador_de_cursos.html')