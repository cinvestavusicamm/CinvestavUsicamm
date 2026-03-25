from django.shortcuts import render, redirect

def perfil_docente(request):
    if request.session.get('usuario_rol') !='Docente':
        return redirect('sesion')
    return render(request, 'perfil_docente.html') 