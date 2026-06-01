from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService

@requiere_rol(ROLE_GENERADOR)
def estadisticas_cursos(request):
    return render(request, 'generador_cursos/estadisticas_de_cursos.html', VistasBdService.contexto_generador(request))
