# utils/error_handlers.py
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def error_400(request, exception):
    logger.warning(f"400 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_400.html', {
        'error_code': 400,
        'error_title': 'Solicitud incorrecta',
        'error_message': 'La solicitud no pudo ser procesada',
        'error_description': 'Verifica los datos enviados e intenta nuevamente'
    }, status=400)

def error_401(request, exception):
    logger.warning(f"401 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_401.html', {
        'error_code':401,
        'error_title': 'No autorizado',
        'error_message': 'Necesitas iniciar sesion para acceder a esta página',
        'error_description': 'Por favor, inicia sesión e intenta nuevamente'
    }, status=401)

def error_402(request, exception):
    logger.warning(f"402 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_402.html', {
        'error_code':402,
        'error_title': 'Pago requerido',
        'error_message': 'Esta página requiere un pago para acceder',
        'error_description': 'Por favor, realiza el pago e intenta nuevamente'
    }, status=402)

def error_403(request, exception):
    logger.warning(f"403 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_403.html', {
        'error_code': 403,
        'error_title': 'Acceso denegado',
        'error_message': 'No tienes permiso para acceder a esta página',
        'error_description': 'Si crees que esto es un error, contacta al administrador'
    }, status=403)

def error_404(request, exception):
    logger.warning(f"404 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_404.html', {
        'error_code': 404,
        'error_title': 'Página no encontrada',
        'error_message': 'Lo sentimos, la página que buscas no existe o ha sido movida.',
        'error_description': 'Verifica la URL o vuelve al inicio'
    }, status=404)

def error_405 (request, exception):
    logger.warning(f"405 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_405.html', {
        'error_code': 405,
        'error_title': 'Método no permitido',
        'error_message': 'El método HTTP utilizado no está permitido para esta URL.',
        'error_description': 'Verifica el método HTTP y vuelve a intentarlo'
    }, status=405)

def error_408 (request, exception):
    logger.warning(f"408 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_408.html',{
        'error_code': 408,
        'error_title': 'Tiempo de espera agotado',
        'error_message': 'La solicitud ha tardado demasiado en procesarse.',
        'error_description': 'Intenta recargar la página o vuelve a intentarlo más tarde.'
    }, status=408)

def error_410 (request, exception):
    logger.warning(f"410 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_410.html', {
        'error_code': 410,
        'error_title': 'Recurso no disponible',
        'error_message': 'El recurso que buscas ya no esta disponible.',
        'error_description': 'Es posible que el recurso haya sido eliminado o movido permanentemente.'

    }, status=410)

def error_413 (request, exception):
    logger.warning(f"413 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_413.html', {
        'error_code': 413,
        'error_title': 'Archivo demasiado grande',
        'error_message': 'El archivo que intentas subir excede el límite permitido.',
        'error_description': 'Intenta subir un archivo más pequeño o contacta al administrador para aumentar el límite.'
    }, status=413)

def error_429 (request, exception):
    logger.warning(f"429 Error en: {request.path} - {exception}")
    return render(request, 'Errores/error_429.html',{
        'error_code': 429,
        'error_title': 'Demasiadas solicitudes',
        'error_message': 'Has enviado demasiadas solicitudes en un corto período de tiempo.',
        'error_description': 'Por favor, espera un momento antes de intentar nuevamente.'
    }, status=429)

def error_500(request):
    logger.error(f"500 Error en: {request.path}")
    return render(request, 'Errores/error_500.html', {
        'error_code': 500,
        'error_title': 'Error interno del servidor',
        'error_message': 'Ha ocurrido un error inesperado',
        'error_description': 'Nuestro equipo ha sido notificado. Por favor, intenta más tarde.'
    }, status=500)



