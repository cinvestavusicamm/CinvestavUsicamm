from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import (
    ROLE_GENERADOR,
    ESTADO_BORRADOR,
    ESTADO_APROBADO,
    reconocer_estado_curso,
)
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.services.curso_service import CursoService, CursoInvalido
from apps.users.services.generacion_ia_service import (
    generar_curso_ia as servicio_generar_curso_ia,
    GeneracionIAError,
)
from apps.users.services.foro_service import ForoService
import json
import logging

logger = logging.getLogger(__name__)

@requiere_rol(ROLE_GENERADOR)
def cursos(request):
    return render(request, 'generador_cursos/mis_cursos.html', VistasBdService.contexto_generador(request))
@requiere_rol(ROLE_GENERADOR)
@require_http_methods(["GET"])
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
    
# El orden importa: requiere_rol va debajo de require_http_methods, asi que se
# evalua primero y un usuario sin rol recibe su 403 antes de que la vista llegue
# a mirar el metodo HTTP.
@requiere_rol(ROLE_GENERADOR)
@require_http_methods(["POST"])
def crear_curso_generador(request):
    usuario_id = request.session.get('usuario_id')
    try:
        datos = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'El cuerpo de la peticion no es JSON valido'}, status=400)

    if not isinstance(datos, dict):
        return JsonResponse({'error': 'Se esperaba un objeto JSON'}, status=400)

    # El contenido se valida antes de crear nada: si se creara la fila y el
    # contenido resultara demasiado grande, el curso quedaria guardado con un
    # 400 en la cara del usuario.
    contenido = datos.get('contenido')
    estado = datos.get('estado', ESTADO_BORRADOR)
    generado_con_ia = datos.get('generado_con_ia', False)
    # Un curso que nace de la IA no puede nacer aprobado: la aprobacion es un
    # acto de revision posterior, no algo que el cliente pueda pedir en el
    # mismo POST que crea el curso. Si llega Aprobado, se guarda como Borrador.
    if generado_con_ia and reconocer_estado_curso(estado) == ESTADO_APROBADO:
        estado = ESTADO_BORRADOR
    try:
        if contenido is not None:
            contenido = CursoService.validar_contenido(contenido)
        curso = CursoService.crear_curso(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', ''),
            docente_id=usuario_id,
            estado=estado,
            generado_con_ia=generado_con_ia
        )
    except CursoInvalido as e:
        # 400 con el campo concreto, no un 500 por IntegrityError.
        return JsonResponse(
            {'error': e.mensaje, 'campo': e.campo}, status=400
        )
    except Exception:
        # La excepcion va al log con su traza; al cliente solo un mensaje que
        # no enseñe nombres de tabla, columnas ni credenciales.
        logger.exception('Error creando curso para el usuario %s', usuario_id)
        return JsonResponse(
            {'error': 'No se pudo crear el curso. Intentalo de nuevo.'}, status=500
        )

    if contenido is not None:
        # Ya validado arriba; aqui solo se escribe.
        curso.contenido_json = contenido
        curso.save(update_fields=['contenido_json', 'updated_at'])

    return JsonResponse({
        'success': True,
        'mensaje': 'Curso creado exitosamente',
        'curso_id': curso.id_curso,
        'titulo': curso.titulo
    })


@requiere_rol(ROLE_GENERADOR)
@require_http_methods(["PUT"])
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
    
@requiere_rol(ROLE_GENERADOR)
@require_http_methods(["DELETE"])
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


# La generacion tarda decenas de segundos (Ollama en local): el timeout lo
# gestiona ia_service_core y Django lo espera con IA_SERVICE_TIMEOUT. No se
# guarda nada aqui; devuelve el contenido para que la interfaz lo pinte y el
# usuario lo revise antes de guardarlo por el endpoint de creacion.
@requiere_rol(ROLE_GENERADOR)
@require_http_methods(["POST"])
def generar_curso_con_ia(request):
    try:
        datos = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'El cuerpo de la peticion no es JSON valido'}, status=400)

    if not isinstance(datos, dict):
        return JsonResponse({'error': 'Se esperaba un objeto JSON'}, status=400)

    peticion = (datos.get('peticion') or datos.get('prompt') or '').strip()
    if not peticion:
        return JsonResponse({'error': 'Describe el curso que quieres generar'}, status=400)

    try:
        contenido = servicio_generar_curso_ia(peticion)
    except CursoInvalido as e:
        # La IA devolvio algo con la forma equivocada: 400 con el campo.
        return JsonResponse({'error': e.mensaje, 'campo': e.campo}, status=400)
    except GeneracionIAError as e:
        return JsonResponse({'error': e.mensaje}, status=e.status)
    except Exception:
        logger.exception('Error generando curso con IA')
        return JsonResponse(
            {'error': 'No se pudo generar el curso. Intentalo de nuevo.'}, status=500
        )

    return JsonResponse({'success': True, 'contenido': contenido})