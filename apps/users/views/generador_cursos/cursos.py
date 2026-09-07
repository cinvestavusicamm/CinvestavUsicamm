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
def cursos(request):
    return render(request, 'generador_cursos/mis_cursos.html', VistasBdService.contexto_generador(request))
@require_http_methods(["GET"])
@requiere_rol(ROLE_GENERADOR)
def obtener_curso_generador(request, curso_id):
    try:
        usuario_id = request.session.get('usuario_id')
        curso = CursoService.obtener_curso_por_id(curso_id)
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No autorizado'}, status=403)

        return JsonResponse({
            'id': curso.id_curso,
            'titulo': curso.titulo,
            'descripcion': curso.descripcion,
            'estado': curso.estado,
            'tipo': 'vertical',  # o deduce de algún campo, si no lo tienes pon un valor por defecto
            'duracion': '40 horas',  # igual, puedes calcularlo o dejarlo fijo
            'generado_con_ia': curso.generado_con_ia,
            'contenido': curso.contenido_json
        })
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_GENERADOR)
def crear_curso_generador(request):
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')

        curso = CursoService.crear_curso(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', ''),
            docente_id=usuario_id,
            estado=datos.get('estado', 'Borrador'),
            generado_con_ia=datos.get('generado_con_ia', False)
        )

        if 'contenido' in datos:
            curso.contenido_json = datos['contenido']  # ya es dict
            curso.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Curso creado exitosamente',
            'curso_id': curso.id_curso,
            'titulo': curso.titulo
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["PUT"])
@requiere_rol(ROLE_GENERADOR)
def actualizar_curso_generador(request, curso_id):
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')

        curso = CursoService.obtener_curso_por_id(curso_id)
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para editar este curso'}, status=403)

        curso_actualizado = CursoService.actualizar_curso(
            curso_id=curso_id,
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion'),
            estado=datos.get('estado')
        )

        if 'contenido' in datos:
            curso_actualizado.contenido_json = datos['contenido']
            curso_actualizado.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Curso actualizado exitosamente',
            'curso_id': curso_actualizado.id_curso
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_http_methods(["DELETE"])
@requiere_rol(ROLE_GENERADOR)
def eliminar_curso_generador(request, curso_id):
    try:
        usuario_id = request.session.get('usuario_id')
        curso = CursoService.obtener_curso_por_id(curso_id)
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        CursoService.desactivar_curso(curso_id)  # o eliminar físicamente si prefieres
        return JsonResponse({'success': True, 'mensaje': 'Curso eliminado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)