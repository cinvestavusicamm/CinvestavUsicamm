from django.shortcuts import render, redirect

def dashboard(request):
    if request.session.get('usuario_rol') != 'evaluador':
        return redirect('sesion') 
    
    return render(request, 'evaluador/dashboard.html')
