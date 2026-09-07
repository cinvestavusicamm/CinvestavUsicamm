from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario, Curso, Foro, PostForo
from apps.users.services.curso_service import CursoService
from apps.users.services.foro_service import ForoService
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService
import json

@requiere_rol(ROLE_DOCENTE)
def panel_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso = procesos.first() if procesos else None

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'total_cursos': cursos.count(),
        'proceso': proceso,
    }
    return render(request, 'docente/panel_docente.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_DOCENTE)
def crear_curso_panel(request):
    """Crear nuevo curso desde el panel del docente"""
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
            'curso_id': curso.id_curso,
            'titulo': curso.titulo
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_curso_panel(request, curso_id):
    """Actualizar curso existente"""
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
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso actualizado exitosamente',
            'curso_id': curso_actualizado.id_curso
        })
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
@requiere_rol(ROLE_DOCENTE)
def eliminar_curso_panel(request, curso_id):
    """Eliminar curso"""
    try:
        usuario_id = request.session.get('usuario_id')
        
        curso = CursoService.obtener_curso_por_id(curso_id)
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para eliminar este curso'}, status=403)
        
        CursoService.desactivar_curso(curso_id)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso eliminado exitosamente'
        })
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_DOCENTE)
def crear_foro_panel(request):
    """Crear nuevo foro"""
    try:
        datos = json.loads(request.body)
        
        foro = ForoService.crear_foro(
            curso_id=datos.get('curso_id'),
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', '')
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Foro creado exitosamente',
            'foro_id': foro.id_foro,
            'titulo': foro.titulo
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@requiere_rol(ROLE_DOCENTE)
def crear_post_panel(request):
    """Crear nuevo post en foro"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        post = ForoService.crear_post(
            foro_id=datos.get('foro_id'),
            autor_id=usuario_id,
            contenido=datos.get('contenido')
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Post creado exitosamente',
            'post_id': post.id_post
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)