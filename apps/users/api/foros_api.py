"""
API endpoints para ms_orchestrator - Gestión de foros
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.users.models import Foro


@csrf_exempt
@require_http_methods(["GET"])
def api_listar_foros(request):
    """API endpoint para listar foros"""
    curso_id = request.GET.get('curso_id')
    
    if curso_id:
        foros = list(Foro.objects.filter(curso_id=curso_id).values())
    else:
        foros = list(Foro.objects.all().values())
    
    return JsonResponse({
        'success': True,
        'data': foros,
        'count': len(foros)
    })
