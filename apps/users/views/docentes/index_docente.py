from django.shortcuts import render, redirect

def index_docente(request):
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('sesion')
    return render(request, 'index_docente.html')
