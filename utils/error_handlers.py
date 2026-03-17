# utils/error_handlers.py
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def error_404(request, exception):
    """Página no encontrada"""
    logger.warning(f"404 Error en: {request.path} - {exception}")
    return render(request, 'error_404.html', {
        'error_code': 404,
        'error_title': 'Página no encontrada',
        'error_message': 'Lo sentimos, la página que buscas no existe o ha sido movida.',
        'error_description': 'Verifica la URL o vuelve al inicio'
    }, status=404)

def error_500(request):
    """Error interno del servidor"""
    logger.error(f"500 Error en: {request.path}")
    return render(request, 'error_500.html', {
        'error_code': 500,
        'error_title': 'Error interno del servidor',
        'error_message': 'Ha ocurrido un error inesperado',
        'error_description': 'Nuestro equipo ha sido notificado. Por favor, intenta más tarde.'
    }, status=500)

def error_403(request, exception):
    """Acceso prohibido"""
    logger.warning(f"403 Error en: {request.path} - {exception}")
    return render(request, 'error_403.html', {
        'error_code': 403,
        'error_title': 'Acceso denegado',
        'error_message': 'No tienes permiso para acceder a esta página',
        'error_description': 'Si crees que esto es un error, contacta al administrador'
    }, status=403)

def error_400(request, exception):
    """Solicitud incorrecta"""
    logger.warning(f"400 Error en: {request.path} - {exception}")
    return render(request, 'error_400.html', {
        'error_code': 400,
        'error_title': 'Solicitud incorrecta',
        'error_message': 'La solicitud no pudo ser procesada',
        'error_description': 'Verifica los datos enviados e intenta nuevamente'
    }, status=400)