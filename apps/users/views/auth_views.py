from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from ..models import Institucion, Usuario, Rol
from apps.users.constants import (ROLE_ADMIN,ROLE_DOCENTE,ROLE_EVALUADOR,ROLE_GENERADOR,)
from apps.users.services.login_security_service import LoginSecurityService
import re
import logging
import time

logger = logging.getLogger(__name__)

def sesion(request):
    if request.method == 'POST':
        curp = request.POST.get('curp', '').strip().upper()
        password = request.POST['password']
        ip = LoginSecurityService.obtener_ip(request)
        
        time.sleep(0.5)
        
        curp_pattern = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$')
        if not curp_pattern.match(curp):
            logger.warning(f"CURP inválida desde IP: {ip}")
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')

        if LoginSecurityService.esta_bloqueado(curp, ip):
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')

        usuario_valido = False
        rol_usuario = None
        id_usuario = None
        nombre_usuario = None
        
        try:
            usuario = Usuario.objects.select_related('rol').get(curp=curp)
            if usuario.activo and usuario.check_password(password):
                usuario_valido = True
                rol_usuario = usuario.rol.nombre_rol.strip()
                id_usuario = usuario.id_usuario
                nombre_usuario = usuario.nombre
        except Usuario.DoesNotExist:
            pass
        
        if not usuario_valido:
            LoginSecurityService.registrar_fallo(curp, ip)
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('sesion')
        
        LoginSecurityService.limpiar_intentos(curp, ip)
        
        request.session.flush()
        
        request.session['usuario_id'] = id_usuario
        request.session['usuario_nombre'] = nombre_usuario
        request.session['usuario_rol'] = rol_usuario
        
        usuario.ultimo_acceso = timezone.now()
        usuario.save(update_fields=['ultimo_acceso'])
        
        if rol_usuario == ROLE_ADMIN:
            return redirect('panel_admin')
        elif rol_usuario == ROLE_DOCENTE:
            return redirect('Docente:panel_docente')
        elif rol_usuario == ROLE_EVALUADOR:
            return redirect('evaluador:dashboard')
        elif rol_usuario == ROLE_GENERADOR:
            return redirect('generador_cursos:index_generador')
        else:
            messages.error(request, 'Error en el sistema. Contacte al administrador.')
            return redirect('sesion')

    return render(request, 'docente/sesion.html')

def registro(request):
    instituciones = Institucion.objects.filter(activo=True)
    
    if request.method == 'GET':
        return render(request, 'docente/registro.html', {
            'instituciones': instituciones,
            'datos_form': {}
        })
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        curp = request.POST.get('curp', '').strip().upper()
        correo = request.POST.get('correo', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        institucion_id = request.POST.get('institucion_id', '')
        
        datos_form = {
            'nombre': nombre,
            'apellido_paterno': apellido_paterno,
            'apellido_materno': apellido_materno,
            'curp': curp,
            'correo': correo,
            'institucion_id': institucion_id,
        }
        
        errores = []
        
        if not nombre:
            errores.append('El nombre es obligatorio')
        if not apellido_paterno:
            errores.append('El apellido paterno es obligatorio')
        if not curp:
            errores.append('La CURP es obligatoria')
        if not correo:
            errores.append('El correo electrónico es obligatorio')
        if not password1:
            errores.append('La contraseña es obligatoria')
        if not institucion_id:
            errores.append('Debe seleccionar una institución')
        
        curp_pattern = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$')
        if curp and not curp_pattern.match(curp):
            errores.append('Formato de CURP inválido. Ejemplo: GODE561231HDFRPR09')
        
        if curp and len(curp) != 18:
            errores.append('La CURP debe tener exactamente 18 caracteres')
        
        if password1:
            if len(password1) < 8:
                errores.append('La contraseña debe tener al menos 8 caracteres')
            
            if not re.search(r'[A-Z]', password1):
                errores.append('La contraseña debe contener al menos una letra mayúscula')
            
            if not re.search(r'[a-z]', password1):
                errores.append('La contraseña debe contener al menos una letra minúscula')
            
            if not re.search(r'\d', password1):
                errores.append('La contraseña debe contener al menos un número')
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
                errores.append('La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>)')
        
        if password1 and password2 and password1 != password2:
            errores.append('Las contraseñas no coinciden')
        
        if correo and '@' not in correo:
            errores.append('Ingrese un correo electrónico válido')
        
        if correo and Usuario.objects.filter(correo=correo).exists():
            errores.append('Ya existe un usuario registrado con este correo electrónico')
        
        if curp and Usuario.objects.filter(curp=curp).exists():
            errores.append('Ya existe un usuario registrado con esta CURP')
        
        if institucion_id:
            try:
                institucion = Institucion.objects.get(id_institucion=institucion_id, activo=True)
            except Institucion.DoesNotExist:
                errores.append('La institución seleccionada no es válida')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            
            return render(request, 'docente/registro.html', {
                'instituciones': instituciones,
                'datos_form': datos_form
            })
        
        try:
            rol_docente = Rol.objects.get(nombre_rol=ROLE_DOCENTE)
            
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno if apellido_materno else '',
                correo=correo,
                contrasena=make_password(password1),
                curp=curp,
                rol=rol_docente,
                institucion_id=institucion_id,
                activo=True
            )
            
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('sesion')
            
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            messages.error(request, 'Ocurrió un error al crear la cuenta. Por favor, intenta nuevamente.')
            
            return render(request, 'docente/registro.html', {
                'instituciones': instituciones,
                'datos_form': datos_form
            })
    
    return redirect('registro')

def cerrar_sesion(request):
    request.session.flush()
    return redirect('sesion')