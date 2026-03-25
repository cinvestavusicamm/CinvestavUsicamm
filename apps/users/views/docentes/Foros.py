from django.shortcuts import render, redirect

def foros (request):
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('sesion')
    return render(request, 'Foros.html')