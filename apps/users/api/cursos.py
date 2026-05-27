"""
API endpoints para gestión de cursos
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.curso_service import CursoService
from apps.users.models import Curso


@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_GENERADOR)
def crear_curso_api(request):
    """
    Crea un nuevo curso generado por IA con toda su estructura
    
    Expected JSON:
    {
        "titulo": "string",
        "descripcion": "string",
        "contenido": {
            "modulos": [...],
            "preguntas_audio": [...],
            "relaciones": [...],
            "examen_final": [...]
        }
    }
    """
    try:
        datos = json.loads(request.body)
        
        # Validar datos requeridos
        if not datos.get('titulo'):
            return JsonResponse({'error': 'El título es requerido'}, status=400)
        
        # Crear el curso
        curso = CursoService.crear_curso(
            titulo=datos['titulo'],
            descripcion=datos.get('descripcion', ''),
            docente_id=request.user.id,
            estado='Borrador',
            generado_con_ia=True
        )
        
        # Guardar el contenido en descripción (temporal) o campo JSON si existe
        if 'contenido' in datos:
            curso.contenido_json = json.dumps(datos['contenido'])
            curso.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso creado exitosamente',
            'curso_id': curso.id_curso,
            'titulo': curso.titulo
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["PUT"])
@requiere_rol(ROLE_GENERADOR)
def actualizar_curso_api(request, curso_id):
    """
    Actualiza un curso existente
    """
    try:
        datos = json.loads(request.body)
        
        # Verificar que el usuario es dueño del curso
        curso = CursoService.obtener_curso_por_id(curso_id)
        if curso.docente_id != request.user.id:
            return JsonResponse({'error': 'No tienes permiso para editar este curso'}, status=403)
        
        # Actualizar
        curso_actualizado = CursoService.actualizar_curso(
            curso_id=curso_id,
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion'),
            estado=datos.get('estado')
        )
        
        # Si hay contenido, guardarlo
        if 'contenido' in datos:
            curso_actualizado.contenido_json = json.dumps(datos['contenido'])
            curso_actualizado.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso actualizado exitosamente',
            'curso_id': curso_actualizado.id_curso
        })
        
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
