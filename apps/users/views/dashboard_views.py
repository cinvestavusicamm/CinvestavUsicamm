from django.shortcuts import render, redirect
from ..models import Institucion, Usuario, Rol
from ..form import UsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def dashboard(request):
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    return render(request, 'index.html')

def panel_admin(request):
    if not request.session.get('usuario_id'):
        return redirect('sesion')

    roles = Rol.objects.all()
    instituciones = Institucion.objects.all()
    form = UsuarioForm()
    
    return render(request, 'paneladm.html', {
        'roles': roles,
        'instituciones': instituciones,
        'form': form
    })

@csrf_exempt
def agregar_usuario_ajax(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'})

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            error_msg = ', '.join([f"{k}: {v[0]}" for k,v in form.errors.items()])
            return JsonResponse({'success': False, 'error': error_msg})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
