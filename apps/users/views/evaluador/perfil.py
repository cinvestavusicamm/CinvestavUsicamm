from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_EVALUADOR)
def perfil(request):
    return render(request, 'evaluador/perfil.html', VistasBdService.contexto_evaluador(request))
