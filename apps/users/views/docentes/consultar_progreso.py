from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.curso_service import CursoService
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService

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