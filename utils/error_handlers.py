# utils/error_handlers.py
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def get_user_context(request):
    """Obtener contexto del usuario para páginas de error."""
    user = request.user if request.user.is_authenticated else None
    
    # Determinar rol del usuario
    user_role = None
    redirect_url = '/'
    
    if user:
        if hasattr(user, 'rol'):
            user_role = user.rol
        elif hasattr(user, 'groups') and user.groups.exists():
            user_role = user.groups.first().name
        
        # Redirección según rol
        if user_role == 'ADMINISTRADOR' or user_role == 'ADMIN':
            redirect_url = '/administrador/dashboard/'
        elif user_role == 'GENERADOR':
            redirect_url = '/generador/dashboard/'
        elif user_role == 'DOCENTE':
            redirect_url = '/docente/panel-docente/'
        elif user_role == 'EVALUADOR':
            redirect_url = '/evaluador/dashboard/'
        else:
            redirect_url = '/dashboard/'
    
    # Si no está autenticado, redirigir a login
    if not user:
        redirect_url = '/sesion/'
    
    return {
        'user': user,
        'user_role': user_role,
        'redirect_url': redirect_url,
        'is_authenticated': user is not None
    }

def generate_ai_error_message(error_code, error_title, user_role=None):
    """Generar mensaje de error personalizado usando IA."""
    # Mensajes base según tipo de error
    base_messages = {
        400: "Calma, {} La solicitud que enviaste no pudo ser procesada, pero esto no es tu culpa. El sistema está diseñado para protegerte.",
        401: "Hola {} Necesitas iniciar sesión para continuar. Esto es normal y por seguridad del sistema.",
        403: "Entendido {} No tienes acceso a esta sección por ahora. Esto es para proteger la información del sistema.",
        404: "No te preocupes {} La página que buscas no existe o fue movida. Esto puede pasar y no es tu culpa.",
        405: "Tranquilo {} El método de solicitud no está permitido. El sistema está protegiendo la integridad de los datos.",
        408: "Paciencia {} La solicitud tardó demasiado. Los servidores están trabajando para ti.",
        410: "Entendido {} Este recurso ya no está disponible. El sistema se está actualizando constantemente.",
        413: "Calma {} El archivo es demasiado grande. Esto es para proteger el rendimiento del sistema.",
        429: "Paciencia {} Has enviado muchas solicitudes. El sistema está protegiendo su estabilidad.",
        500: "No te preocupes {} Ocurrió un error interno. Nuestro equipo técnico ya fue notificado y está trabajando en solucionarlo."
    }
    
    # Determinar saludo según rol
    greeting = "usuario"
    if user_role:
        if user_role == 'ADMINISTRADOR' or user_role == 'ADMIN':
            greeting = "administrador"
        elif user_role == 'GENERADOR':
            greeting = "generador"
        elif user_role == 'DOCENTE':
            greeting = "maestra/o"
        elif user_role == 'EVALUADOR':
            greeting = "evaluador"
    
    # Obtener mensaje base
    message = base_messages.get(error_code, "Ocurrió un error inesperado. No te preocupes, no es tu culpa.")
    
    # Formatear mensaje
    return message.format(greeting)

def error_400(request, exception):
    logger.warning(f"400 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 400,
        'error_title': 'Solicitud incorrecta',
        'error_message': 'La solicitud no pudo ser procesada',
        'error_description': 'Verifica los datos enviados e intenta nuevamente',
        'ai_message': generate_ai_error_message(400, 'Solicitud incorrecta', context.get('user_role'))
    })
    return render(request, 'Errores/error_400.html', context, status=400)

def error_401(request, exception):
    logger.warning(f"401 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 401,
        'error_title': 'No autorizado',
        'error_message': 'Necesitas iniciar sesion para acceder a esta página',
        'error_description': 'Por favor, inicia sesión e intenta nuevamente',
        'ai_message': generate_ai_error_message(401, 'No autorizado', context.get('user_role'))
    })
    return render(request, 'Errores/error_401.html', context, status=401)

def error_402(request, exception):
    logger.warning(f"402 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 402,
        'error_title': 'Pago requerido',
        'error_message': 'Esta página requiere un pago para acceder',
        'error_description': 'Por favor, realiza el pago e intenta nuevamente',
        'ai_message': generate_ai_error_message(402, 'Pago requerido', context.get('user_role'))
    })
    return render(request, 'Errores/error_402.html', context, status=402)

def error_403(request, exception):
    logger.warning(f"403 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 403,
        'error_title': 'Acceso denegado',
        'error_message': 'No tienes permiso para acceder a esta página',
        'error_description': 'Si crees que esto es un error, contacta al administrador',
        'ai_message': generate_ai_error_message(403, 'Acceso denegado', context.get('user_role'))
    })
    return render(request, 'Errores/error_403.html', context, status=403)

def error_404(request, exception):
    logger.warning(f"404 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 404,
        'error_title': 'Página no encontrada',
        'error_message': 'Lo sentimos, la página que buscas no existe o ha sido movida.',
        'error_description': 'Verifica la URL o vuelve al inicio',
        'ai_message': generate_ai_error_message(404, 'Página no encontrada', context.get('user_role'))
    })
    return render(request, 'Errores/error_404.html', context, status=404)

def error_405 (request, exception):
    logger.warning(f"405 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 405,
        'error_title': 'Método no permitido',
        'error_message': 'El método HTTP utilizado no está permitido para esta URL.',
        'error_description': 'Verifica el método HTTP y vuelve a intentarlo',
        'ai_message': generate_ai_error_message(405, 'Método no permitido', context.get('user_role'))
    })
    return render(request, 'Errores/error_405.html', context, status=405)

def error_408 (request, exception):
    logger.warning(f"408 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 408,
        'error_title': 'Tiempo de espera agotado',
        'error_message': 'La solicitud ha tardado demasiado en procesarse.',
        'error_description': 'Intenta recargar la página o vuelve a intentarlo más tarde.',
        'ai_message': generate_ai_error_message(408, 'Tiempo de espera agotado', context.get('user_role'))
    })
    return render(request, 'Errores/error_408.html', context, status=408)

def error_410 (request, exception):
    logger.warning(f"410 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 410,
        'error_title': 'Recurso no disponible',
        'error_message': 'El recurso que buscas ya no esta disponible.',
        'error_description': 'Es posible que el recurso haya sido eliminado o movido permanentemente.',
        'ai_message': generate_ai_error_message(410, 'Recurso no disponible', context.get('user_role'))
    })
    return render(request, 'Errores/error_410.html', context, status=410)

def error_413 (request, exception):
    logger.warning(f"413 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 413,
        'error_title': 'Archivo demasiado grande',
        'error_message': 'El archivo que intentas subir excede el límite permitido.',
        'error_description': 'Intenta subir un archivo más pequeño o contacta al administrador para aumentar el límite.',
        'ai_message': generate_ai_error_message(413, 'Archivo demasiado grande', context.get('user_role'))
    })
    return render(request, 'Errores/error_413.html', context, status=413)

def error_429 (request, exception):
    logger.warning(f"429 Error en: {request.path} - {exception}")
    context = get_user_context(request)
    context.update({
        'error_code': 429,
        'error_title': 'Demasiadas solicitudes',
        'error_message': 'Has enviado demasiadas solicitudes en un corto período de tiempo.',
        'error_description': 'Por favor, espera un momento antes de intentar nuevamente.',
        'ai_message': generate_ai_error_message(429, 'Demasiadas solicitudes', context.get('user_role'))
    })
    return render(request, 'Errores/error_429.html', context, status=429)

def error_500(request):
    logger.error(f"500 Error en: {request.path}")
    context = get_user_context(request)
    context.update({
        'error_code': 500,
        'error_title': 'Error interno del servidor',
        'error_message': 'Ha ocurrido un error inesperado',
        'error_description': 'Nuestro equipo ha sido notificado. Por favor, intenta más tarde.',
        'ai_message': generate_ai_error_message(500, 'Error interno del servidor', context.get('user_role'))
    })
    return render(request, 'Errores/error_500.html', context, status=500)



