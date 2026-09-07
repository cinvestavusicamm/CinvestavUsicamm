from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_EVALUADOR)
def evaluaciones(request):
    """
    Vista que muestra todos los cursos/evaluaciones disponibles para el evaluador.
    Permite filtrar, buscar y gestionar evaluaciones.
    """
    context = VistasBdService.contexto_evaluador(request)
    return render(request, 'Evaluador/evaluaciones.html', context)
