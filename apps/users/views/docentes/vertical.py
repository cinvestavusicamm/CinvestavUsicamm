from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.curso_service import CursoService
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService

@requiere_rol(ROLE_DOCENTE)
def promociones_vertical(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    # Obtener procesos de escalafón del docente (filtrar por tipo vertical si existe)
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso_vertical = None
    
    # Buscar proceso de tipo promoción vertical
    for proceso in procesos:
        if proceso.tipo_proceso and 'vertical' in proceso.tipo_proceso.lower():
            proceso_vertical = proceso
            break
    
    # Si no hay proceso vertical específico, usar el más reciente
    if not proceso_vertical and procesos:
        proceso_vertical = procesos.first()
    
    # Extraer datos multifactores del proceso
    datos_multifactores = {}
    if proceso_vertical and proceso_vertical.datos_multifactores:
        datos_multifactores = proceso_vertical.datos_multifactores
    
    # Calcular puntajes y métricas para promoción vertical
    puntaje_antiguedad = datos_multifactores.get('puntaje_antiguedad', 0)
    puntaje_grado_academico = datos_multifactores.get('puntaje_grado_academico', 0)
    puntaje_cursos = datos_multifactores.get('puntaje_cursos', 0)
    puntaje_total = datos_multifactores.get('puntaje_multifactorial', 0)
    horas_formacion = datos_multifactores.get('horas_formacion', 0)
    horas_faltantes = max(0, 200 - horas_formacion)  # Calcular horas faltantes para completar 200
    
    # Calcular porcentajes para las barras de progreso
    porcentaje_antiguedad = round((puntaje_antiguedad / 30) * 100) if puntaje_antiguedad > 0 else 0
    porcentaje_grado_academico = round((puntaje_grado_academico / 15) * 100) if puntaje_grado_academico > 0 else 0
    porcentaje_cursos = round((puntaje_cursos / 15) * 100) if puntaje_cursos > 0 else 0
    
    # Información de fechas importantes
    fechas_importantes = []
    if proceso_vertical:
        if proceso_vertical.ciclo_escolar:
            fechas_importantes.append({
                'evento': 'Ciclo Escolar',
                'periodo': proceso_vertical.ciclo_escolar,
                'estado': proceso_vertical.estatus
            })
    
    # Agregar fechas de cursos
    for curso in cursos[:3]:
        if curso.fecha_aprobacion:
            fechas_importantes.append({
                'evento': curso.titulo,
                'periodo': curso.fecha_aprobacion.strftime('%d %b %Y') if curso.fecha_aprobacion else 'N/A',
                'estado': curso.estado
            })

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'total_cursos': cursos.count(),
        'proceso': proceso_vertical,
        'datos_multifactores': datos_multifactores,
        'puntaje_antiguedad': puntaje_antiguedad,
        'puntaje_grado_academico': puntaje_grado_academico,
        'puntaje_cursos': puntaje_cursos,
        'puntaje_total': puntaje_total,
        'horas_formacion': horas_formacion,
        'horas_faltantes': horas_faltantes,
        'porcentaje_antiguedad': porcentaje_antiguedad,
        'porcentaje_grado_academico': porcentaje_grado_academico,
        'porcentaje_cursos': porcentaje_cursos,
        'fechas_importantes': fechas_importantes,
    }
    return render(request, 'docente/vertical.html', context)