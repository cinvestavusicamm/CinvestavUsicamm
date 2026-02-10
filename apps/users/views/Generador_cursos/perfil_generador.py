from django.shortcuts import render, redirect
def perfil_generador (request):
    if request.session.get('usuario_rol') != 'Generador':
        return redirect('sesion')
    return render(request, 'Generador_cursos/mi_perfil.html')