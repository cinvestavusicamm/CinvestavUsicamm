"""
API endpoints para ms_orchestrator - Gestión de cursos
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.users.api.cursos import crear_curso_api, actualizar_curso_api


@csrf_exempt
@require_http_methods(["GET"])
def api_listar_cursos(request):
    """API endpoint para listar cursos"""
    from apps.users.services.curso_service import CursoService
    
    docente_id = request.GET.get('docente_id')
    if docente_id:
        cursos = CursoService.listar_cursos_por_docente(docente_id)
    else:
        from apps.users.models import Curso
        cursos = list(Curso.objects.all().values())
    
    return JsonResponse({
        'success': True,
        'data': cursos,
        'count': len(cursos)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_crear_curso(request):
    """API endpoint para crear curso"""
    return crear_curso_api(request)


@csrf_exempt
@require_http_methods(["POST"])
def api_actualizar_curso(request, curso_id):
    """API endpoint para actualizar curso"""
    return actualizar_curso_api(request, curso_id)
