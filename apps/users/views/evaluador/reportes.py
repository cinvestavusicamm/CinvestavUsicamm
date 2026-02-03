from django.shortcuts import render, redirect

def reportes(request):
    if request.session.get('usuario_rol') != 'evaluador':
        return redirect('sesion') 
    return render(request, 'evaluador/reportes.html')