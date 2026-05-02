from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from ..models import Institucion, Usuario, Rol
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from apps.users.constants import (ROLE_ADMIN,ROLE_DOCENTE,ROLE_EVALUADOR,ROLE_GENERADOR,)
from apps.users.services.login_security_service import LoginSecurityService

def sesion(request):
    if request.method == 'POST':
        curp = request.POST['curp']
        password = request.POST['password']
        ip= LoginSecurityService.obtener_ip(request)

        if LoginSecurityService.esta_bloqueado(curp, ip):
            messages.error(request, 'Demasiados intentos fallidos. Intente nuevamente más tarde.')
            return redirect('sesion')

        try:
            usuario = Usuario.objects.select_related('rol').get(curp=curp)
        except Usuario.DoesNotExist:
            LoginSecurityService.registrar_fallo(curp, ip)
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')

        if not usuario.activo:
            LoginSecurityService.registrar_fallo(curp, ip)
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')

        if usuario.check_password(password):
            LoginSecurityService.limpiar_intentos(curp, ip)
            request.session.flush()

            rol = usuario.rol.nombre_rol.strip()

            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = rol

            usuario.ultimo_acceso = timezone.now()
            usuario.save(update_fields=['ultimo_acceso'])

            if rol == ROLE_ADMIN:
                return redirect('panel_admin')

            elif rol == ROLE_DOCENTE:
                return redirect('Docente:panel_docente')

            elif rol == ROLE_EVALUADOR:
                return redirect('evaluador:dashboard')

            elif rol == ROLE_GENERADOR:
                return redirect('generador_cursos:index_generador') 

            else:
                messages.error(request, f'Rol no reconocido: {rol}')
                return redirect('sesion')
        LoginSecurityService.registrar_fallo(curp, ip)
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

        rol = Rol.objects.get(nombre_rol=ROLE_DOCENTE)

        Usuario.objects.create(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo=correo,
            contrasena=make_password(password1),
            curp=curp,
            rol=rol,
            institucion_id=institucion_id,
            activo=True
        )

        messages.success(request, 'Cuenta creada correctamente')
        return redirect('sesion')

    return render(request, 'registro.html', {
    'instituciones': instituciones
})

def cerrar_sesion(request):
    request.session.flush()
    return redirect('sesion')

