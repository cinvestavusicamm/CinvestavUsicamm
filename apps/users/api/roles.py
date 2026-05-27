"""
API endpoints para datos por rol
"""
from django.views.decorators.http import require_GET
from apps.users.config.constants import ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
from apps.users.infrastructure.api_response import respuesta_ok
from apps.users.services.permisos import requiere_rol
from apps.users.services.vistas_bd_service import VistasBdService


def _usuario_payload(usuario):
    """Formatea datos de usuario para respuesta JSON"""
    if not usuario:
        return None

    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido_paterno": usuario.apellido_paterno,
        "apellido_materno": usuario.apellido_materno,
        "correo": usuario.correo,
        "curp": usuario.curp,
        "rol": getattr(usuario.rol, "nombre_rol", None),
        "institucion": getattr(usuario.institucion, "nombre", None),
    }


def _curso_payload(curso):
    """Formatea datos de curso para respuesta JSON"""
    return {
        "id_curso": curso.id_curso,
        "titulo": curso.titulo,
        "descripcion": curso.descripcion,
        "estado": curso.estado,
        "generado_con_ia": curso.generado_con_ia,
        "version": curso.version,
        "fecha_creacion": curso.fecha_creacion.isoformat() if curso.fecha_creacion else None,
        "fecha_aprobacion": curso.fecha_aprobacion.isoformat() if curso.fecha_aprobacion else None,
    }


def _proceso_payload(proceso):
    """Formatea datos de proceso para respuesta JSON"""
    return {
        "folio": proceso.folio,
        "tipo_proceso": proceso.tipo_proceso,
        "ciclo_escolar": proceso.ciclo_escolar,
        "estatus": proceso.estatus,
        "estado": getattr(proceso.estado, "nombre", None),
        "fecha_registro": proceso.fecha_registro.isoformat() if proceso.fecha_registro else None,
    }


def _aprobacion_payload(aprobacion):
    """Formatea datos de aprobación para respuesta JSON"""
    return {
        "id_proceso": aprobacion.id_proceso,
        "curso": _curso_payload(aprobacion.curso),
        "evaluador": _usuario_payload(aprobacion.evaluador),
        "iteracion": aprobacion.iteracion,
        "decision": aprobacion.decision,
        "comentarios": aprobacion.comentarios,
        "fecha_revision": aprobacion.fecha_revision.isoformat() if aprobacion.fecha_revision else None,
    }


@require_GET
@requiere_rol(ROLE_DOCENTE)
def datos_docente_ajax(request):
    """API endpoint para obtener datos del docente"""
    context = VistasBdService.contexto_docente(request)
    return respuesta_ok(
        request,
        "Datos del docente obtenidos correctamente",
        {
            "usuario": _usuario_payload(context["usuario"]),
            "total_cursos": context["total_cursos"],
            "total_procesos": context["total_procesos"],
            "cursos": [_curso_payload(curso) for curso in context["cursos"]],
            "procesos": [_proceso_payload(proceso) for proceso in context["procesos"]],
        },
    )


@require_GET
@requiere_rol(ROLE_EVALUADOR)
def datos_evaluador_ajax(request):
    """API endpoint para obtener datos del evaluador"""
    context = VistasBdService.contexto_evaluador(request)
    return respuesta_ok(
        request,
        "Datos del evaluador obtenidos correctamente",
        {
            "usuario": _usuario_payload(context["usuario"]),
            "total_cursos": context["total_cursos"],
            "total_pendientes": context["total_pendientes"],
            "total_aprobaciones": context["total_aprobaciones"],
            "total_aprobaciones_evaluador": context["total_aprobaciones_evaluador"],
            "total_procesos": context["total_procesos"],
            "cursos_pendientes": [
                _curso_payload(curso) for curso in context["cursos_pendientes"]
            ],
            "aprobaciones": [
                _aprobacion_payload(aprobacion) for aprobacion in context["aprobaciones"]
            ],
        },
    )


@require_GET
@requiere_rol(ROLE_GENERADOR)
def datos_generador_ajax(request):
    """API endpoint para obtener datos del generador"""
    context = VistasBdService.contexto_generador(request)
    return respuesta_ok(
        request,
        "Datos del generador obtenidos correctamente",
        {
            "usuario": _usuario_payload(context["usuario"]),
            "total_cursos": context["total_cursos"],
            "total_borradores": context["total_borradores"],
            "total_pendientes": context["total_pendientes"],
            "total_aprobados": context["total_aprobados"],
            "estadisticas_estados": context["estadisticas_estados"],
            "cursos": [_curso_payload(curso) for curso in context["cursos"]],
            "aprobaciones": [
                _aprobacion_payload(aprobacion) for aprobacion in context["aprobaciones"]
            ],
        },
    )
