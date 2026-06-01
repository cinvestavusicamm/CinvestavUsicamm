from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import logging
from apps.users.models import Rol, Institucion, Usuario
from apps.users.forms.usuario_forms import UsuarioForm
from apps.users.infrastructure.api_response import respuesta_ok, respuesta_error
from apps.users.config.constants import ROLE_ADMIN
from apps.users.services.bitacora_service import BitacoraService
from apps.users.services.user_service import UserService
import json
from django.contrib.auth.hashers import make_password


logger = logging.getLogger(__name__)


def _registrar_bitacora(request, tipo_evento, descripcion, detalles=None):
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

def crear_admin(request):
    if request.method == 'POST':
        rol_admin = Rol.objects.get(nombre_rol=ROLE_ADMIN)
        institucion = Institucion.objects.get(id_institucion=request.POST['institucion'])

        usuario = UserService.crear_usuario({
            'nombre': request.POST['nombre'],
            'apellido_paterno': request.POST['apellido_paterno'],
            'apellido_materno': request.POST.get('apellido_materno', ''),
            'correo': request.POST['correo'],
            'contrasena': request.POST['password'],
            'curp': request.POST['curp'],
            'rol': rol_admin,
            'institucion': institucion,
            'activo': True,
        })

        _registrar_bitacora(
            request,
            'ADMIN_CREADO',
            f'Creó al administrador {usuario.id_usuario}',
            {'usuario_creado': usuario.id_usuario},
        )

        messages.success(request, 'Administrador creado correctamente')
        return redirect('sesion')

    instituciones = Institucion.objects.all()
    return render(request, 'administrador/crear_admin.html', {'instituciones': instituciones})


def agregar_usuario_ajax(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    try:
        required_fields = ['nombre', 'apellido_paterno', 'correo', 'contrasena', 'curp', 'rol', 'institucion']
        missing = [field for field in required_fields if not request.POST.get(field)]
        
        if missing:
            return JsonResponse({
                'success': False, 
                'error': f'Campos requeridos faltantes: {", ".join(missing)}'
            }, status=400)
        
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
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def toggle_usuario(request, id):
    if not request.session.get('usuario_id'):
        return respuesta_error(request, 'No autorizado')

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


def editar_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    try:
        usuario = Usuario.objects.get(id_usuario=id)
        
        usuario.nombre = request.POST.get('nombre', usuario.nombre)
        usuario.apellido_paterno = request.POST.get('apellido_paterno', usuario.apellido_paterno)
        usuario.apellido_materno = request.POST.get('apellido_materno', usuario.apellido_materno)
        usuario.correo = request.POST.get('correo', usuario.correo)
        usuario.curp = request.POST.get('curp', usuario.curp)
        
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
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def obtener_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=401)

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
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


