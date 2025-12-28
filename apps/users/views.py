from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Institucion, Usuario, Rol
from django.contrib.auth.hashers import make_password

def index(request):
    return render(request, 'users/index.html')


def sesion(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        password = request.POST['password']

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')

        if usuario.check_password(password):  
            request.session['usuario_id'] = usuario.id_usuario
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'sesion.html')

def registro(request):
    instituciones = Institucion.objects.filter(activo=True)

    if request.method == 'POST':
        nombre = request.POST['nombre']
        apellido_paterno = request.POST['apellido_paterno']
        apellido_materno = request.POST.get('apellido_materno')
        curp = request.POST['curp']
        correo = request.POST['correo']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        institucion_id = request.POST['institucion_id']

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('registro')

        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, 'El correo ya está registrado')
            return redirect('registro')

        if Usuario.objects.filter(curp=curp).exists():
            messages.error(request, 'La CURP ya está registrada')
            return redirect('registro')

        rol = Rol.objects.get(nombre_rol='Usuario')

        Usuario.objects.create(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo=correo,
            contraseña=make_password(password1),
            curp=curp,
            rol=rol,
            institucion_id=institucion_id,
            activo=True
        )

        messages.success(request, 'Cuenta creada correctamente')
        return redirect('sesion')

    return render(request, 'resgistro.html', {
        'instituciones': instituciones
    })


def cerrar_sesion(request):
    logout(request)
    return redirect('sesion')


@login_required
def dashboard(request):
    return render(request, 'dash.html')


@login_required
def panel_admin(request):
    return render(request, 'paneladm.html')


@login_required
def chat(request):
    return render(request, 'chat.html')


@login_required
def prueba(request):
    return render(request, 'prueba.html')
