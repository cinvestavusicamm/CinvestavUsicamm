from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.curso_service import CursoService
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService

@requiere_rol(ROLE_DOCENTE)
def promociones_horizontal(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    # Obtener procesos de escalafón del docente (filtrar por tipo horizontal si existe)
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso_horizontal = None
    
    # Buscar proceso de tipo promoción horizontal
    for proceso in procesos:
        if proceso.tipo_proceso and 'horizontal' in proceso.tipo_proceso.lower():
            proceso_horizontal = proceso
            break
    
    # Si no hay proceso horizontal específico, usar el más reciente
    if not proceso_horizontal and procesos:
        proceso_horizontal = procesos.first()
    
    # Extraer datos multifactores del proceso
    datos_multifactores = {}
    if proceso_horizontal and proceso_horizontal.datos_multifactores:
        datos_multifactores = proceso_horizontal.datos_multifactores
    
    # Calcular puntajes y métricas para promoción horizontal
    puntaje_formacion_profesional = datos_multifactores.get('puntaje_formacion_profesional', 0)
    puntaje_antiguedad = datos_multifactores.get('puntaje_antiguedad', 0)
    puntaje_cursos = datos_multifactores.get('puntaje_cursos', 0)
    puntaje_total = datos_multifactores.get('puntaje_multifactorial', 0)
    horas_formacion = datos_multifactores.get('horas_formacion', 0)
    
    # Información de fechas importantes del proceso horizontal
    fechas_proceso = []
    if proceso_horizontal:
        if proceso_horizontal.ciclo_escolar:
            fechas_proceso.append({
                'evento': 'Ciclo Escolar',
                'periodo': proceso_horizontal.ciclo_escolar,
                'estado': proceso_horizontal.estatus
            })
        
        # Simular etapas del proceso horizontal
        etapas = [
            {'numero': 1, 'nombre': 'Convocatoria y Acuerdos', 'descripcion': 'Publicación del acuerdo y convocatoria en la página de USICAMM. Generación de usuario en Plataforma VENUS.', 'estado': 'completado'},
            {'numero': 2, 'nombre': 'Registro y Verificación', 'descripcion': 'Generación de cita y entrega documental para validación de los elementos multifactoriales.', 'estado': 'completado'},
            {'numero': 3, 'nombre': 'Apreciación de Conocimientos', 'descripcion': 'Aplicación del instrumento de apreciación de conocimientos y aptitudes (CENEVAL). Revise su sede y horario.', 'estado': 'actual'},
            {'numero': 4, 'nombre': 'Consulta de Resultados', 'descripcion': 'Publicación de resultados por participante y periodo para recurso de reconsideración.', 'estado': 'pendiente'},
            {'numero': 5, 'nombre': 'Asignación de Incentivos', 'descripcion': 'Publicación del listado nominal ordenado de resultados y evento público de asignación.', 'estado': 'pendiente'},
        ]
    else:
        etapas = []

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'total_cursos': cursos.count(),
        'proceso': proceso_horizontal,
        'datos_multifactores': datos_multifactores,
        'puntaje_formacion_profesional': puntaje_formacion_profesional,
        'puntaje_antiguedad': puntaje_antiguedad,
        'puntaje_cursos': puntaje_cursos,
        'puntaje_total': puntaje_total,
        'horas_formacion': horas_formacion,
        'fechas_proceso': fechas_proceso,
        'etapas': etapas,
    }
    return render(request, 'docente/estatus_horizontal.html', context)