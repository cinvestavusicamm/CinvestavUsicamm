"""
Health check endpoint para Django Backend
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint para el backend Django"""
    return JsonResponse({
        'status': 'ok',
        'service': 'django_backend',
        'version': '1.0.0'
    })
