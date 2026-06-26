from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.services.curso_service import CursoService
from apps.users.services.foro_service import ForoService
import json

@requiere_rol(ROLE_GENERADOR)
def index_generador(request):
    return render(request, 'generador_cursos/index_generador_de_cursos.html', VistasBdService.contexto_generador(request))

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_GENERADOR)
def crear_curso_index(request):
    """Crear curso desde index del generador"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        curso = CursoService.crear_curso(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', ''),
            docente_id=usuario_id,
            estado='Borrador',
            generado_con_ia=datos.get('generado_con_ia', False)
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso creado exitosamente',
            'curso_id': curso.id_curso
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
