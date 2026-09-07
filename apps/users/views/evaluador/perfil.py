from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_EVALUADOR)
def perfil(request):
    """
    Vista del perfil del evaluador.
    Muestra información personal del usuario conectado a la base de datos.
    """
    context = VistasBdService.contexto_evaluador(request)
    return render(request, 'Evaluador/perfil.html', context)
