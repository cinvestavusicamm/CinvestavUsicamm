from django.shortcuts import render, redirect
from django.contrib import messages
import logging
from apps.users.models import Rol, Institucion, Usuario
from ..forms import UsuarioForm
from apps.users.utils.api_response import respuesta_ok, respuesta_error
from apps.users.constants import ROLE_ADMIN
from apps.users.services.bitacora_service import BitacoraService
from apps.users.services.user_service import UserService


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
        return respuesta_error(request, 'No autorizado')

    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            usuario = UserService.crear_usuario({
                'nombre': form.cleaned_data['nombre'],
                'apellido_paterno': form.cleaned_data['apellido_paterno'],
                'apellido_materno': form.cleaned_data.get('apellido_materno'),
                'correo': form.cleaned_data['correo'],
                'contrasena': form.cleaned_data['contrasena'],
                'curp': form.cleaned_data['curp'],
                'rol': form.cleaned_data['rol'],
                'institucion': form.cleaned_data['institucion'],
                'activo': True,
            })

            _registrar_bitacora(
                request,
                'USUARIO_CREADO',
                f'Creó al usuario {usuario.id_usuario}',
                {'usuario_creado': usuario.id_usuario},
            )

            return respuesta_ok(request, 'Usuario agregado correctamente')

        return respuesta_error(request, form.errors)

    return respuesta_error(request, 'Método no permitido')



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
        return respuesta_error(request, 'No autorizado')

    if request.method == 'POST':
        try:
            usuario = UserService.editar_usuario(id, {
                'nombre': request.POST.get('nombre'),
                'apellido_paterno': request.POST.get('apellido_paterno'),
                'apellido_materno': request.POST.get('apellido_materno'),
                'correo': request.POST.get('correo'),
                'curp': request.POST.get('curp'),
                'rol': request.POST.get('rol'),
                'institucion': request.POST.get('institucion'),
                'contrasena': request.POST.get('contrasena'),
            })

            _registrar_bitacora(
                request,
                'USUARIO_EDITADO',
                f'Editó al usuario {usuario.id_usuario}',
                {'usuario_editado': usuario.id_usuario},
            )

            return respuesta_ok(request, 'Usuario actualizado correctamente')

        except Exception as e:
            return respuesta_error(request, str(e))

    return respuesta_error(request, 'Método no permitido')

def obtener_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return respuesta_error(request, 'No autorizado')

    try:
        usuario = UserService.obtener_usuario(id)

        return respuesta_ok(request, 'Usuario obtenido correctamente', {
            'success': True,
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno,
            'correo': usuario.correo,
            'curp': usuario.curp,
            'rol': usuario.rol.id_rol,
            'institucion': usuario.institucion.id_institucion
        })

    except Usuario.DoesNotExist:
        return respuesta_error(request, 'Usuario no encontrado')



