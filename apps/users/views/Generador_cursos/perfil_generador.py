from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.models import Usuario
import json

@requiere_rol(ROLE_GENERADOR)
def perfil_generador(request):
    return render(request, 'generador_cursos/mi_perfil.html', VistasBdService.contexto_generador(request))

@require_http_methods(["PUT"])
@requiere_rol(ROLE_GENERADOR)
def actualizar_perfil_generador(request):
    """Actualizar perfil del generador"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        if datos.get('nombre'):
            usuario.nombre = datos['nombre']
        if datos.get('correo'):
            usuario.correo = datos['correo']
        if datos.get('telefono'):
            usuario.telefono = datos['telefono']
        
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Perfil actualizado exitosamente'
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
