from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_EVALUADOR)
def banco_preguntas(request):
    """
    Vista del banco de preguntas para el evaluador.
    Muestra cursos/evaluaciones disponibles como preguntas para revisión.
    Nota: No existe modelo específico para banco de preguntas, se usa Curso.
    """
    context = VistasBdService.contexto_evaluador(request)
    return render(request, 'Evaluador/banco_preguntas.html', context)
