from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE
from apps.users.models import Usuario

@requiere_rol(ROLE_DOCENTE)
def promociones_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    
    context = {
        'usuario': usuario
    }
    return render(request, 'Rutas_promociones.html', context)
