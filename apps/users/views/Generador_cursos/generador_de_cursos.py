from django.shortcuts import render, redirect

def generador_de_cursos(request):
    if request.session.get('usuario_rol') != 'Generador':
        return redirect('sesion')
    
    return render(request, 'Generador_cursos/generador_de_cursos.html')