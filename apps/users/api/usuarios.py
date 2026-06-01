"""
API endpoints para gestión de usuarios
"""
from django.http import JsonResponse
import logging
from apps.users.models import Usuario, Rol, Institucion
from apps.users.services.user_service import UserService
from apps.users.services.bitacora_service import BitacoraService
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_ADMIN
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


def _registrar_bitacora(request, tipo_evento, descripcion, detalles=None):
    """Helper para registrar eventos en bitácora"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return
    
    try:
        BitacoraService.registrar(
            usuario_id=usuario_id,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            request=request,
            detalles=detalles,
        )
    except Exception as exc:
        logger.warning("No se pudo registrar bitácora: %s", exc)


def _check_rate_limit(request, endpoint_name, max_attempts=10, ttl=3600):
    """Helper para verificar rate limiting"""
    ip = request.META.get('REMOTE_ADDR', '')
    key = f"rate_limit:{endpoint_name}:{ip}"
    
    attempts = cache.get(key, 0)
    
    if attempts >= max_attempts:
        security_logger.warning(f"Rate limit excedido para {endpoint_name} desde IP: {ip}")
        return False
    
    cache.set(key, attempts + 1, ttl)
    return True


def _validate_field_length(value, field_name, max_length):
    """Helper para validar longitud de campos"""
    if value and len(value) > max_length:
        return f'{field_name} demasiado largo (máximo {max_length} caracteres)'
    return None


@csrf_exempt
@requiere_rol(ROLE_ADMIN)
def agregar_usuario_ajax(request):
    """API endpoint para agregar un nuevo usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    if not _check_rate_limit(request, 'agregar_usuario'):
        return JsonResponse({'success': False, 'error': 'Demasiados intentos. Intente más tarde.'}, status=429)

    try:
        required_fields = ['nombre', 'apellido_paterno', 'correo', 'contrasena', 'curp', 'rol', 'institucion']
        missing = [field for field in required_fields if not request.POST.get(field)]
        
        if missing:
            return JsonResponse({
                'success': False, 
                'error': f'Campos requeridos faltantes: {", ".join(missing)}'
            }, status=400)
        
        # Validar longitudes de campos
        nombre = request.POST.get('nombre', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        correo = request.POST.get('correo', '').strip()
        curp = request.POST.get('curp', '').strip()
        
        length_errors = []
        length_errors.append(_validate_field_length(nombre, 'Nombre', 100))
        length_errors.append(_validate_field_length(apellido_paterno, 'Apellido paterno', 100))
        length_errors.append(_validate_field_length(apellido_materno, 'Apellido materno', 100))
        length_errors.append(_validate_field_length(correo, 'Correo', 255))
        length_errors.append(_validate_field_length(curp, 'CURP', 18))
        
        length_errors = [err for err in length_errors if err]
        if length_errors:
            return JsonResponse({'success': False, 'error': '; '.join(length_errors)}, status=400)
        
        try:
            rol = Rol.objects.get(id_rol=request.POST.get('rol'))
            institucion = Institucion.objects.get(id_institucion=request.POST.get('institucion'))
        except Rol.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Rol no válido'}, status=400)
        except Institucion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Institución no válida'}, status=400)
        
        if Usuario.objects.filter(curp=request.POST.get('curp')).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un usuario con esta CURP'}, status=400)
        
        if Usuario.objects.filter(correo=request.POST.get('correo')).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un usuario con este correo'}, status=400)
        
        usuario = UserService.crear_usuario({
            'nombre': request.POST.get('nombre'),
            'apellido_paterno': request.POST.get('apellido_paterno'),
            'apellido_materno': request.POST.get('apellido_materno', ''),
            'correo': request.POST.get('correo'),
            'contrasena': request.POST.get('contrasena'),
            'curp': request.POST.get('curp'),
            'rol': rol,
            'institucion': institucion,
            'activo': True,
        })
        
        _registrar_bitacora(
            request,
            'USUARIO_CREADO',
            f'Creó al usuario {usuario.id_usuario}',
            {'usuario_creado': usuario.id_usuario},
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario agregado correctamente',
            'usuario_id': usuario.id_usuario
        })
        
    except Exception as e:
        logger.error(f"Error creando usuario: {str(e)}", exc_info=True)
        security_logger.warning(f"Error al crear usuario desde IP: {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor. Contacte al administrador.'}, status=500)


@csrf_exempt
@requiere_rol(ROLE_ADMIN)
def toggle_usuario(request, id):
    """API endpoint para activar/desactivar un usuario"""
    from apps.users.infrastructure.api_response import respuesta_error, respuesta_ok
    
    if request.method != 'POST':
        return respuesta_error(request, 'Método no permitido')

    usuario_actual = request.session.get('usuario_id')

    if int(id) == int(usuario_actual):
        return respuesta_error(request, 'No puedes desactivar tu propia cuenta')

    try:
        usuario = UserService.alternar_activo(id)

        _registrar_bitacora(
            request,
            'USUARIO_ACTUALIZADO',
            f'Cambió el estado del usuario {usuario.id_usuario}',
            {
                'usuario_actualizado': usuario.id_usuario,
                'activo': usuario.activo,
            },
        )

        contadores = UserService.obtener_contadores()

        return respuesta_ok(request, 'Usuario desactivado correctamente', {
            'activo': usuario.activo,
            'contadores': contadores,
        })

    except Usuario.DoesNotExist:
        return respuesta_error(request, 'Usuario no encontrado')


@csrf_exempt
@requiere_rol(ROLE_ADMIN)
def editar_usuario_ajax(request, id):
    """API endpoint para editar un usuario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    if not _check_rate_limit(request, 'editar_usuario'):
        return JsonResponse({'success': False, 'error': 'Demasiados intentos. Intente más tarde.'}, status=429)

    try:
        usuario = Usuario.objects.get(id_usuario=id)
        
        nombre = request.POST.get('nombre', usuario.nombre)
        apellido_paterno = request.POST.get('apellido_paterno', usuario.apellido_paterno)
        apellido_materno = request.POST.get('apellido_materno', usuario.apellido_materno)
        correo = request.POST.get('correo', usuario.correo)
        curp = request.POST.get('curp', usuario.curp)
        
        # Validar longitudes de campos
        length_errors = []
        length_errors.append(_validate_field_length(nombre, 'Nombre', 100))
        length_errors.append(_validate_field_length(apellido_paterno, 'Apellido paterno', 100))
        length_errors.append(_validate_field_length(apellido_materno, 'Apellido materno', 100))
        length_errors.append(_validate_field_length(correo, 'Correo', 255))
        length_errors.append(_validate_field_length(curp, 'CURP', 18))
        
        length_errors = [err for err in length_errors if err]
        if length_errors:
            return JsonResponse({'success': False, 'error': '; '.join(length_errors)}, status=400)
        
        usuario.nombre = nombre
        usuario.apellido_paterno = apellido_paterno
        usuario.apellido_materno = apellido_materno
        usuario.correo = correo
        usuario.curp = curp
        
        rol_id = request.POST.get('rol')
        if rol_id:
            try:
                usuario.rol = Rol.objects.get(id_rol=rol_id)
            except Rol.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Rol no válido'}, status=400)
        
        institucion_id = request.POST.get('institucion')
        if institucion_id:
            try:
                usuario.institucion = Institucion.objects.get(id_institucion=institucion_id)
            except Institucion.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Institución no válida'}, status=400)
        
        nueva_contrasena = request.POST.get('contrasena')
        if nueva_contrasena and nueva_contrasena.strip():
            contrasena_actual = request.POST.get('contrasena_actual')
            if not contrasena_actual or not usuario.check_password(contrasena_actual):
                security_logger.warning(f"Intento de cambiar contraseña sin contraseña actual para usuario {id} desde IP: {request.META.get('REMOTE_ADDR')}")
                return JsonResponse({'success': False, 'error': 'La contraseña actual es requerida para cambiar la contraseña'}, status=400)
            usuario.contrasena = make_password(nueva_contrasena)
        
        usuario.save()
        
        _registrar_bitacora(
            request,
            'USUARIO_EDITADO',
            f'Editó al usuario {usuario.id_usuario}',
            {'usuario_editado': usuario.id_usuario},
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })
        
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error editando usuario: {str(e)}", exc_info=True)
        security_logger.warning(f"Error al editar usuario {id} desde IP: {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor. Contacte al administrador.'}, status=500)


@csrf_exempt
@requiere_rol(ROLE_ADMIN)
def obtener_usuario_ajax(request, id):
    """API endpoint para obtener datos de un usuario"""

    try:
        usuario = UserService.obtener_usuario(id)
        
        return JsonResponse({
            'success': True,
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno or '',
            'correo': usuario.correo,
            'curp': usuario.curp,
            'rol': usuario.rol.id_rol,
            'institucion': usuario.institucion.id_institucion
        })

    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        security_logger.warning(f"Error al obtener usuario {id} desde IP: {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'success': False, 'error': 'Error interno del servidor. Contacte al administrador.'}, status=500)
