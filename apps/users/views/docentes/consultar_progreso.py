from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.curso_service import CursoService
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService
import json

@requiere_rol(ROLE_DOCENTE)
def consultar_progreso(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso_actual = procesos.first() if procesos else None
    puntaje_actual = 0
    horas_formacion = 0
    datos_multifactores = {}
    
    if proceso_actual and proceso_actual.datos_multifactores:
        datos = proceso_actual.datos_multifactores
        datos_multifactores = datos
        puntaje_actual = datos.get('puntaje_multifactorial', 0)
        horas_formacion = datos.get('horas_formacion', 0)
    
    # Enriquecer datos de cursos con información de progreso
    cursos_con_progreso = []
    for curso in cursos:
        # Calcular progreso simulado basado en estado y contenido
        progreso = 0
        if curso.estado == 'Aprobado':
            progreso = 100
        elif curso.estado == 'Publicado':
            progreso = 100
        elif curso.estado == 'En Progreso':
            progreso = 50
        elif curso.estado == 'Borrador':
            progreso = 10
        
        # Calcular puntaje del curso
        puntaje_curso = 0
        if curso.contenido_json:
            puntaje_curso = curso.contenido_json.get('puntaje', 0)
        
        cursos_con_progreso.append({
            'curso': curso,
            'progreso': progreso,
            'puntaje': puntaje_curso,
            'estado': curso.estado,
            'fecha_creacion': curso.fecha_creacion,
            'fecha_aprobacion': curso.fecha_aprobacion,
        })
    
    # Calcular estadísticas generales
    total_cursos_completados = sum(1 for c in cursos_con_progreso if c['progreso'] == 100)
    total_cursos_en_progreso = sum(1 for c in cursos_con_progreso if 0 < c['progreso'] < 100)
    total_cursos_pendientes = sum(1 for c in cursos_con_progreso if c['progreso'] == 0)
    
    # Calcular porcentaje general de formación
    porcentaje_formacion = 0
    if cursos:
        porcentaje_formacion = sum(c['progreso'] for c in cursos_con_progreso) / len(cursos)
    
    # Evidencias del portafolio (simuladas desde datos multifactores)
    evidencias = {
        'titulo_profesional': datos_multifactores.get('titulo_validado', False),
        'hoja_servicios': datos_multifactores.get('hoja_servicios_validada', False),
        'cursos_formacion': datos_multifactores.get('cursos_validados', False),
        'posgrado': datos_multifactores.get('posgrado_validado', False),
        'horas_acumuladas': horas_formacion,
        'horas_requeridas': 200,  # Valor estándar
    }

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'cursos_con_progreso': cursos_con_progreso,
        'total_cursos': cursos.count(),
        'total_cursos_completados': total_cursos_completados,
        'total_cursos_en_progreso': total_cursos_en_progreso,
        'total_cursos_pendientes': total_cursos_pendientes,
        'proceso_actual': proceso_actual,
        'puntaje_actual': puntaje_actual,
        'horas_formacion': horas_formacion,
        'porcentaje_formacion': round(porcentaje_formacion, 1),
        'datos_multifactores': datos_multifactores,
        'evidencias': evidencias,
    }
    return render(request, 'docente/Consulta_progreso.html', context)

@require_http_methods(["PUT"])
@requiere_rol(ROLE_DOCENTE)
def actualizar_progreso_docente(request):
    """Actualizar datos de progreso del docente"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
        proceso = procesos.first() if procesos else None
        
        if not proceso:
            return JsonResponse({'error': 'No hay proceso de escalafón activo'}, status=404)
        
        # Actualizar datos multifactores
        if proceso.datos_multifactores is None:
            proceso.datos_multifactores = {}
        
        if 'puntaje_multifactorial' in datos:
            proceso.datos_multifactores['puntaje_multifactorial'] = datos['puntaje_multifactorial']
        if 'horas_formacion' in datos:
            proceso.datos_multifactores['horas_formacion'] = datos['horas_formacion']
        
        proceso.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Progreso actualizado exitosamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@requiere_rol(ROLE_DOCENTE)
def ver_certificado(request, curso_id):
    """Ver certificado de curso completado"""
    try:
        usuario_id = request.session.get('usuario_id')
        curso = CursoService.obtener_curso_por_id(curso_id)
        
        # Verificar que el curso pertenezca al docente
        if curso.docente_id != usuario_id:
            return JsonResponse({'error': 'No tienes permiso para ver este certificado'}, status=403)
        
        # Verificar que el curso esté completado
        if curso.estado not in ['Aprobado', 'Publicado', 'Completado']:
            return JsonResponse({'error': 'El curso no ha sido completado aún'}, status=400)
        
        # Aquí podrías generar un PDF real del certificado
        # Por ahora, retornamos un mensaje de éxito
        return JsonResponse({
            'success': True,
            'mensaje': f'Certificado disponible para el curso: {curso.titulo}',
            'curso_titulo': curso.titulo,
            'fecha_aprobacion': curso.fecha_aprobacion.strftime('%d/%m/%Y') if curso.fecha_aprobacion else 'N/A'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)