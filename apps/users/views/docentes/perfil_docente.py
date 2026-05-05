from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService

@requiere_rol(ROLE_DOCENTE)
def perfil_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    procesos = ProcesoEscalafonService.obtener_procesos_usuario(usuario_id)
    proceso = procesos.first() if procesos else None

    context = {
        'usuario': usuario,
        'proceso': proceso
    }
    return render(request, 'docente/perfil_docente.html', context)