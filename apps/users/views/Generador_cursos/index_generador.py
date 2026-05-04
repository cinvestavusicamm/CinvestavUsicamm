from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_GENERADOR

@requiere_rol(ROLE_GENERADOR)
def index_generador(request):
    return render(request, 'Generador_cursos/index_generador_de_cursos.html')