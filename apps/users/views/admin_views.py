from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ..models import Usuario, Rol, Institucion

def crear_admin(request):

    # 🔒 SOLO BLOQUEAR SI YA EXISTE UN ADMIN
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
