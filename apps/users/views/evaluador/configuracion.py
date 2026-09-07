import json

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from apps.users.models import Usuario
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@ensure_csrf_cookie
@requiere_rol(ROLE_EVALUADOR)
def configuracion(request):
    """
    Vista de configuración del evaluador.
    Permite editar perfil, seguridad, accesibilidad y preferencias.
    Incluye endpoints para actualizar datos personales y contraseña.
    """
    return render(request, 'Evaluador/configuracion.html', VistasBdService.contexto_evaluador(request))

@require_http_methods(["PUT"])
@requiere_rol(ROLE_EVALUADOR)
def actualizar_perfil_evaluador(request):
    try:
        datos = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=403)

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)

    correo = datos.get('correo')
    telefono = datos.get('telefono')

    if correo is not None:
        correo = correo.strip().lower()
        if correo == '':
            return JsonResponse({'success': False, 'error': 'El correo no puede estar vacío'}, status=400)
        if Usuario.objects.exclude(id_usuario=usuario_id).filter(correo=correo).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un usuario con este correo'}, status=400)
        usuario.correo = correo

    if telefono is not None:
        telefono = telefono.strip()
        usuario.telefono = telefono if telefono != '' else None

    update_fields = []
    if correo is not None:
        update_fields.append('correo')
    if telefono is not None:
        update_fields.append('telefono')

    if update_fields:
        usuario.save(update_fields=update_fields)
    else:
        # No hay cambios que persistir, devolver un resultado exitoso que mantenga la experiencia.
        return JsonResponse({'success': True, 'mensaje': 'No se realizaron cambios'})

    return JsonResponse({'success': True, 'mensaje': 'Perfil actualizado correctamente'})

@require_http_methods(["PUT"])
@requiere_rol(ROLE_EVALUADOR)
def actualizar_contrasena_evaluador(request):
    try:
        datos = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=403)

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)

    actual = datos.get('contrasena_actual', '').strip()
    nueva = datos.get('nueva_contrasena', '').strip()
    confirmar = datos.get('confirmar_contrasena', '').strip()

    if not actual or not nueva or not confirmar:
        return JsonResponse({'success': False, 'error': 'Todos los campos de contraseña son obligatorios'}, status=400)
    if nueva != confirmar:
        return JsonResponse({'success': False, 'error': 'La nueva contraseña no coincide con la confirmación'}, status=400)
    if len(nueva) < 8:
        return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres'}, status=400)
    if not usuario.check_password(actual):
        return JsonResponse({'success': False, 'error': 'Contraseña actual incorrecta'}, status=400)

    usuario.contrasena = make_password(nueva)
    usuario.save(update_fields=['contrasena'])

    return JsonResponse({'success': True, 'mensaje': 'Contraseña actualizada correctamente'})
