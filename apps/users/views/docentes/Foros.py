from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.foro_service import ForoService
from apps.users.services.curso_service import CursoService
import json

@requiere_rol(ROLE_DOCENTE)
def foros(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    foro_items = []
    total_foros = 0
    total_posts = 0
    
    for curso in cursos:
        foros_curso = ForoService.obtener_foros_curso(curso.id_curso)
        total_foros += foros_curso.count()
        
        foros_con_posts = []
        for foro in foros_curso:
            posts_foro = ForoService.obtener_posts_foro(foro.id_foro)
            total_posts += posts_foro.count()
            
            foros_con_posts.append({
                'foro': foro,
                'posts': posts_foro,
                'total_posts': posts_foro.count(),
            })
        
        foro_items.append({
            'curso': curso,
            'foros': foros_con_posts,
            'total_foros_curso': foros_curso.count(),
        })
    
    # Obtener posts recientes del usuario
    posts_usuario = []
    for curso in cursos:
        foros_curso = ForoService.obtener_foros_curso(curso.id_curso)
        for foro in foros_curso:
            posts_foro = ForoService.obtener_posts_foro(foro.id_foro)
            posts_usuario.extend([post for post in posts_foro if post.autor_id == usuario_id])
    
    # Ordenar posts por fecha de publicación
    posts_usuario.sort(key=lambda x: x.fecha_publicacion, reverse=True)
    posts_usuario = posts_usuario[:10]  # Limitar a 10 posts recientes
    
    context = {
        'usuario': usuario,
        'cursos': cursos,
        'foro_items': foro_items,
        'total_foros': total_foros,
        'total_posts': total_posts,
        'posts_usuario': posts_usuario,
        'total_cursos': cursos.count(),
    }
    return render(request, 'docente/Foros.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_DOCENTE)
def crear_foro_docente(request):
    """Crear nuevo foro"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        # Verificar que el curso pertenece al docente
        curso = CursoService.obtener_curso_por_id(datos.get('curso_id'))
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para crear foros en este curso'}, status=403)
        
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

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_foro_docente(request, foro_id):
    """Actualizar foro existente"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        foro = ForoService.obtener_foro_por_id(foro_id)
        curso = CursoService.obtener_curso_por_id(foro.curso_id)
        
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para editar este foro'}, status=403)
        
        foro_actualizado = ForoService.actualizar_foro(
            foro_id=foro_id,
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion')
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Foro actualizado exitosamente',
            'foro_id': foro_actualizado.id_foro
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
@requiere_rol(ROLE_DOCENTE)
def eliminar_foro_docente(request, foro_id):
    """Eliminar foro"""
    try:
        usuario_id = request.session.get('usuario_id')
        
        foro = ForoService.obtener_foro_por_id(foro_id)
        curso = CursoService.obtener_curso_por_id(foro.curso_id)
        
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para eliminar este foro'}, status=403)
        
        ForoService.desactivar_foro(foro_id)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Foro eliminado exitosamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@requiere_rol(ROLE_DOCENTE)
def crear_post_docente(request):
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

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_post_docente(request, post_id):
    """Actualizar post existente"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        post = ForoService.obtener_post_por_id(post_id)
        
        if post.autor_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para editar este post'}, status=403)
        
        post_actualizado = ForoService.actualizar_post(
            post_id=post_id,
            contenido=datos.get('contenido')
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Post actualizado exitosamente',
            'post_id': post_actualizado.id_post
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
@requiere_rol(ROLE_DOCENTE)
def eliminar_post_docente(request, post_id):
    """Eliminar post"""
    try:
        usuario_id = request.session.get('usuario_id')
        
        post = ForoService.obtener_post_por_id(post_id)
        
        if post.autor_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para eliminar este post'}, status=403)
        
        ForoService.eliminar_post(post_id)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Post eliminado exitosamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
