from django.shortcuts import render, redirect

def generador_de_cursos(request):
    if request.session.get('usuario_rol') != 'generador_cursos':
        return redirect('sesion')
    
    return render(request, 'Generador_cursos/generador_de_cursos.html')