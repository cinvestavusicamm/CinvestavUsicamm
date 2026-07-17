from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.services.curso_service import CursoService
import json

@requiere_rol(ROLE_GENERADOR)
def generador_de_cursos(request, curso_id=None):
    context = VistasBdService.contexto_generador(request)
    if curso_id is not None:
        context['curso_id'] = curso_id
    return render(request, 'generador_cursos/generador_de_cursos.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_GENERADOR)
def guardar_curso_generado(request):
    """Guardar curso generado por IA"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        curso = CursoService.crear_curso(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', ''),
            docente_id=usuario_id,
            estado='Borrador',
            generado_con_ia=True
        )
        
        if 'contenido' in datos:
            curso.contenido_json = datos['contenido']
            curso.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso generado guardado exitosamente',
            'curso_id': curso.id_curso
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)