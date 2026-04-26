from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE

@requiere_rol(ROLE_DOCENTE)
def cursos_promociones(request):
    return render(request, 'cursos_promociones.html')