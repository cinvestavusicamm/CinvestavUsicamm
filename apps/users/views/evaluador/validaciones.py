from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.models import ProcesoAprobacionCursos, Curso
from apps.users.services.curso_service import CursoService
import json

@requiere_rol(ROLE_EVALUADOR)
def validaciones(request):
    """
    Vista principal de validaciones para el evaluador.
    Muestra cursos pendientes de revisión y permite aprobar/rechazar.
    """
    context = VistasBdService.contexto_evaluador(request)
    
    # Seleccionar curso actual a validar usando query param si está disponible
    cursos_pendientes = context.get('cursos_pendientes', [])
    curso_id = request.GET.get('curso_id')
    curso_actual = None

    if cursos_pendientes:
        if curso_id:
            curso_actual = next(
                (curso for curso in cursos_pendientes if str(getattr(curso, 'id_curso', '')) == str(curso_id)),
                None
            )
        if not curso_actual:
            curso_actual = cursos_pendientes[0]

    context['curso_actual'] = curso_actual
    return render(request, 'Evaluador/validaciones.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_EVALUADOR)
def aprobar_pregunta(request, pregunta_id):
    """
    Aprueba una pregunta/curso en el proceso de validación
    """
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        comentarios = datos.get('comentarios', '')
        
        # Crear registro de aprobación
        ProcesoAprobacionCursos.objects.create(
            curso_id=datos.get('curso_id'),
            evaluador_id=usuario_id,
            iteracion=datos.get('iteracion', '1'),
            decision='APROBADA',
            comentarios=comentarios,
            fecha_revision=datos.get('fecha_revision')
        )
        
        # Actualizar estado del curso si es necesario
        if datos.get('actualizar_curso'):
            CursoService.actualizar_curso(
                curso_id=datos.get('curso_id'),
                estado='Aprobado'
            )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Pregunta aprobada correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_EVALUADOR)
def rechazar_pregunta(request, pregunta_id):
    """
    Rechaza una pregunta/curso en el proceso de validación
    """
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        comentarios = datos.get('comentarios', '')
        
        if not comentarios.strip():
            return JsonResponse({'error': 'Los comentarios son obligatorios para el rechazo'}, status=400)
        
        # Crear registro de rechazo
        ProcesoAprobacionCursos.objects.create(
            curso_id=datos.get('curso_id'),
            evaluador_id=usuario_id,
            iteracion=datos.get('iteracion', '1'),
            decision='RECHAZADA',
            comentarios=comentarios,
            fecha_revision=datos.get('fecha_revision')
        )
        
        # Actualizar estado del curso
        CursoService.actualizar_curso(
            curso_id=datos.get('curso_id'),
            estado='Rechazado'
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Pregunta rechazada correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_EVALUADOR)
def enviar_revision_pregunta(request, pregunta_id):
    """
    Envía una pregunta/curso a revisión con observaciones
    """
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        comentarios = datos.get('comentarios', '')
        
        if not comentarios.strip():
            return JsonResponse({'error': 'Las observaciones son obligatorias'}, status=400)
        
        # Crear registro de revisión
        ProcesoAprobacionCursos.objects.create(
            curso_id=datos.get('curso_id'),
            evaluador_id=usuario_id,
            iteracion=datos.get('iteracion', '1'),
            decision='EN_REVISION',
            comentarios=comentarios,
            fecha_revision=datos.get('fecha_revision')
        )
        
        # Actualizar estado del curso
        CursoService.actualizar_curso(
            curso_id=datos.get('curso_id'),
            estado='En_Revisión'
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Pregunta enviada a revisión correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
