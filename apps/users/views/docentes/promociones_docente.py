from django.shortcuts import render, redirect

def promociones_docente(request):
    if request.session.get('usuario_rol') != 'Docente':
        return redirect ('sesion')
    return render(request, 'Rutas_promociones.html')

