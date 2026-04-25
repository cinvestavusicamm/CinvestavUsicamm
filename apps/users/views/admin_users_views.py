from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ..models import Usuario, Rol, Institucion
from ..forms import UsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from apps.users.utils.api_response import respuesta_ok, respuesta_error
from apps.users.constants import ROLE_ADMIN

def crear_admin(request):
    if request.method == 'POST':
        rol_admin = Rol.objects.get(nombre_rol=ROLE_ADMIN)
        institucion = Institucion.objects.first()

        Usuario.objects.create(
            nombre=request.POST['nombre'],
            apellido_paterno=request.POST['apellido_paterno'],
            apellido_materno=request.POST.get('apellido_materno', ''),
            correo=request.POST['correo'],
            contrasena=make_password(request.POST['password']),
            curp=request.POST['curp'],
            rol=rol_admin,
            institucion=institucion,
            activo=True
        )

        messages.success(request, 'Administrador creado correctamente')
        return redirect('sesion')

    return render(request, 'crear_admin.html')

def agregar_usuario_ajax(request):
    if not request.session.get('usuario_id'):
        return respuesta_error(request, 'No autorizado')

    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save(commit=False)

            usuario.activo = True
            usuario.save()

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
        usuario = Usuario.objects.get(id_usuario=id)
        usuario.activo = not usuario.activo
        usuario.save(update_fields=['activo'])

        # Opcional: contadores en vivo
        total = Usuario.objects.count()
        activos = Usuario.objects.filter(activo=True).count()
        en_revision = total - activos

        return respuesta_ok(request, 'Usuario desactivado correctamente', {
            'activo': usuario.activo,
            'contadores': {
                'total': total,
                'activos': activos,
                'en_revision': en_revision,
            }
        })

    except Usuario.DoesNotExist:
        return respuesta_error(request, 'Usuario no encontrado')


def editar_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return respuesta_error(request, 'No autorizado')

    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id_usuario=id)
            usuario.nombre = request.POST.get('nombre')
            usuario.apellido_paterno = request.POST.get('apellido_paterno')
            usuario.apellido_materno = request.POST.get('apellido_materno')
            usuario.correo = request.POST.get('correo')
            usuario.curp = request.POST.get('curp')

            from apps.users.models import Rol, Institucion
            rol_nombre = request.POST.get('rol')
            if rol_nombre:
                usuario.rol = Rol.objects.get(nombre_rol=rol_nombre)
            institucion_id = request.POST.get('institucion')
            if institucion_id:
                usuario.institucion = Institucion.objects.get(id_institucion=institucion_id)

            nueva_pass = request.POST.get('contraseña')
            if nueva_pass:  
                usuario.contrasena = make_password(nueva_pass)

            usuario.save()
            return respuesta_ok(request, 'Usuario actualizado correctamente')

        except Exception as e:
            return respuesta_error(request, str(e))

    return respuesta_error(request, 'Método no permitido')

def obtener_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return respuesta_error(request, 'No autorizado')

    try:
        usuario = Usuario.objects.get(id_usuario=id)

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



