from django.shortcuts import render
from django.http import JsonResponse
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.services.curso_service import CursoService
from apps.users.services.foro_service import ForoService

@requiere_rol(ROLE_GENERADOR)
def estadisticas_cursos(request):
    return render(request, 'generador_cursos/estadisticas_de_cursos.html', VistasBdService.contexto_generador(request))

@requiere_rol(ROLE_GENERADOR)
def obtener_estadisticas_api(request):
    """API para obtener estadísticas de cursos"""
    try:
        usuario_id = request.session.get('usuario_id')
        cursos = CursoService.obtener_cursos_docente(usuario_id)
        
        estadisticas = {
            'total_cursos': cursos.count(),
            'cursos_activos': cursos.filter(estado='Activo').count(),
            'cursos_borrador': cursos.filter(estado='Borrador').count(),
            'cursos_completados': cursos.filter(estado='Completado').count(),
        }
        
        return JsonResponse({
            'success': True,
            'estadisticas': estadisticas
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
