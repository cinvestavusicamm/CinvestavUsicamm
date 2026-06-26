from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_EVALUADOR)
def validaciones(request):
    return render(request, 'evaluador/validaciones.html', VistasBdService.contexto_evaluador(request))
