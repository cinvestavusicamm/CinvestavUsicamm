from django.shortcuts import render

from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.permisos import requiere_rol
from apps.users.services.vistas_bd_service import VistasBdService


@requiere_rol(ROLE_EVALUADOR)
def dashboard(request):
    """
    Vista principal del dashboard del evaluador.
    Muestra estadísticas, cursos pendientes de revisión y actividad reciente.
    """
    context = VistasBdService.contexto_evaluador(request)
    return render(request, "Evaluador/dashboard.html", context)
