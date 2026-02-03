from django.shortcuts import render, redirect
def perfil_generador (request):
    if request.session.get('usuario_rol') != 'generador_cursos':
        return redirect('sesion')
    return render(request, 'Generador_cursos/mi_perfil.html')