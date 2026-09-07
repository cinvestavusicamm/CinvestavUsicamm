from django.db.models import Count, Q
from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.models import Curso, ProcesoAprobacionCursos

@requiere_rol(ROLE_EVALUADOR)
def reportes(request):
    """
    Vista de reportes estadísticos para el evaluador.
    Muestra estadísticas detalladas de cursos, aprobaciones y distribuciones.
    """
    context = VistasBdService.contexto_evaluador(request)

    cursos = Curso.objects.order_by('-fecha_creacion')
    aprobaciones = ProcesoAprobacionCursos.objects.select_related('curso').all()

    total_cursos = cursos.count()
    total_pendientes = cursos.filter(
        Q(estado__icontains='pendiente')
        | Q(estado__icontains='revision')
        | Q(estado__icontains='revisión')
    ).count()
    total_aprobados = cursos.filter(estado__icontains='aprob').count()
    total_rechazados = cursos.filter(
        Q(estado__icontains='rechaz')
        | Q(estado__icontains='no aprob')
    ).count()
    total_borradores = cursos.filter(estado__icontains='borrador').count()
    total_revisiones = aprobaciones.count()
    tasa_aprobacion = round((total_aprobados / total_revisiones) * 100, 2) if total_revisiones else 0

    cursos_por_estado = list(
        cursos.values('estado')
        .annotate(total=Count('id_curso'))
        .order_by('-total')[:8]
    )
    max_estado_total = max((item['total'] for item in cursos_por_estado), default=1)
    for item in cursos_por_estado:
        item['bar_percent'] = int(item['total'] * 100 / max_estado_total) if max_estado_total else 0

    decisiones_por_tipo = list(
        aprobaciones.values('decision')
        .annotate(total=Count('id_proceso'))
        .order_by('-total')
    )
    total_decisiones = sum(item['total'] for item in decisiones_por_tipo) or 1
    for item in decisiones_por_tipo:
        item['percent'] = round(item['total'] * 100 / total_decisiones, 2)

    aprobaciones_bd = [
        {
            'id_proceso': aprobacion.id_proceso,
            'curso_id': aprobacion.curso_id,
            'curso_titulo': aprobacion.curso.titulo if aprobacion.curso else '',
            'decision': aprobacion.decision,
            'fecha_revision': aprobacion.fecha_revision.isoformat() if aprobacion.fecha_revision else None,
            'iteracion': aprobacion.iteracion,
        }
        for aprobacion in aprobaciones
    ]

    evaluaciones_bd_full = list(
        cursos.values(
            'id_curso',
            'titulo',
            'estado',
            'fecha_creacion',
            'fecha_aprobacion',
            'contenido_json'
        )
    )

    context.update({
        'reportes_bd': {
            'total_revisiones': total_revisiones,
            'total_cursos': total_cursos,
            'tasa_aprobacion': tasa_aprobacion,
            'total_pendientes': total_pendientes,
            'total_aprobados': total_aprobados,
            'total_rechazados': total_rechazados,
            'total_borradores': total_borradores,
        },
        'reportes_adicionales': {
            'cursos_por_estado': cursos_por_estado,
            'decisiones_por_tipo': decisiones_por_tipo,
        },
        'evaluaciones_bd_full': evaluaciones_bd_full,
        'aprobaciones_bd': aprobaciones_bd,
    })

    return render(request, 'Evaluador/reportes.html', context)
