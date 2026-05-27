"""
API endpoints para ms_orchestrator - Gestión de usuarios
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.users.api.usuarios import agregar_usuario_ajax, editar_usuario_ajax, toggle_usuario, obtener_usuario_ajax


@csrf_exempt
@require_http_methods(["GET"])
def api_get_usuario(request, usuario_id):
    """API endpoint para obtener usuario por ID"""
    return obtener_usuario_ajax(request, usuario_id)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_usuario(request):
    """API endpoint para crear usuario"""
    return agregar_usuario_ajax(request)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_usuario(request, usuario_id):
    """API endpoint para actualizar usuario"""
    return editar_usuario_ajax(request, usuario_id)


@csrf_exempt
@require_http_methods(["POST"])
def api_toggle_usuario(request, usuario_id):
    """API endpoint para alternar estado de usuario"""
    return toggle_usuario(request, usuario_id)
