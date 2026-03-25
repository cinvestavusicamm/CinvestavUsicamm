from django.shortcuts import render, redirect

def panel_docente(request):
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('sesion')
    return render(request, 'panel_docente.html')