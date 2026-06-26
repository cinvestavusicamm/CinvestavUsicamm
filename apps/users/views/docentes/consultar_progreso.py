from django.shortcuts import render
from django.http import JsonResponse
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
    if proceso_actual and proceso_actual.datos_multifactores:
        datos = proceso_actual.datos_multifactores
        puntaje_actual = datos.get('puntaje_multifactorial', 0)
        horas_formacion = datos.get('horas_formacion', 0)

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'total_cursos': cursos.count(),
        'proceso_actual': proceso_actual,
        'puntaje_actual': puntaje_actual,
        'horas_formacion': horas_formacion,
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