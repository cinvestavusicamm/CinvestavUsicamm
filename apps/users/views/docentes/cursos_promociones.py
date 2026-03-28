from django.shortcuts import render, redirect

def cursos_promociones(request):
    if request.session.get('usuario_rol') !='Docente':
        return redirect('sesion')
    return render(request, 'cursos_promociones.html')