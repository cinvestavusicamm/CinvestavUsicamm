from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService
from apps.users.services.user_service import UserService
import json

@requiere_rol(ROLE_DOCENTE)
def perfil_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso = procesos.first() if procesos else None

    context = {
        'usuario': usuario,
        'proceso': proceso
    }
    return render(request, 'docente/Perfil_docente.html', context)

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_perfil_docente(request):
    """Actualizar perfil del docente"""
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

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_contrasena_docente(request):
    """Actualizar contraseña del docente"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        contrasena_actual = datos.get('contrasena_actual')
        nueva_contrasena = datos.get('nueva_contrasena')
        
        if not usuario.check_password(contrasena_actual):
            return JsonResponse({'error': 'Contraseña actual incorrecta'}, status=400)
        
        usuario.set_password(nueva_contrasena)
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Contraseña actualizada exitosamente'
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)