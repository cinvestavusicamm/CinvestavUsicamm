from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_GENERADOR

@requiere_rol(ROLE_GENERADOR)
def cursos(request):
    return render(request, 'Generador_cursos/mis_cursos.html')