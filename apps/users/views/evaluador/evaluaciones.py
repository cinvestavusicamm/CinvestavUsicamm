from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_EVALUADOR

@requiere_rol(ROLE_EVALUADOR)
def evaluaciones(request):
    return render(request, 'evaluador/evaluaciones.html')