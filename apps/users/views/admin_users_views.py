from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ..models import Usuario, Rol, Institucion
from ..forms import UsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

def crear_admin(request):

    if Usuario.objects.filter(rol__nombre_rol='Administrador').exists():
        messages.error(request, 'Ya existe un administrador')
        return redirect('sesion')

    if request.method == 'POST':
        rol_admin = Rol.objects.get(nombre_rol='Administrador')
        institucion = Institucion.objects.first()

        Usuario.objects.create(
            nombre=request.POST['nombre'],
            apellido_paterno=request.POST['apellido_paterno'],
            apellido_materno=request.POST.get('apellido_materno', ''),
            correo=request.POST['correo'],
            contraseña=make_password(request.POST['password']),
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
        return JsonResponse({'success': False, 'error': {'auth': ['No autorizado']}})

    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save(commit=False)

            usuario.activo = True
            usuario.save()

            return JsonResponse({'success': True})

        return JsonResponse({
            'success': False,
            'error': form.errors
        })

    return JsonResponse({'success': False, 'error': {'method': ['Método no permitido']}})



def toggle_usuario(request, id):
    usuario = Usuario.objects.get(id_usuario=id)
    usuario.activo = not usuario.activo
    usuario.save(update_fields=['activo'])
    return JsonResponse({'success': True})

def obtener_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'})

    try:
        usuario = Usuario.objects.get(id_usuario=id)
        data = {
            'success': True,
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno,
            'correo': usuario.correo,
            'curp': usuario.curp,
            'rol': usuario.rol.nombre_rol,
            'institucion': usuario.institucion.id_institucion if usuario.institucion else None,
        }
        return JsonResponse(data)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})

def editar_usuario_ajax(request, id):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'})

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
                usuario.contraseña = make_password(nueva_pass)

            usuario.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


