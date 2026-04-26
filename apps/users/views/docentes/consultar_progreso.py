from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE

@requiere_rol(ROLE_DOCENTE)
def consultar_progreso(request):
    return render(request, 'Consulta_progreso.html')