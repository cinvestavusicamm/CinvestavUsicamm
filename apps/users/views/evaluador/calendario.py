from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_EVALUADOR

@requiere_rol(ROLE_EVALUADOR)
def calendario(request):
    return render(request, 'evaluador/calendario.html')