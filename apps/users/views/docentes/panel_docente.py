from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.curso_service import CursoService

@requiere_rol(ROLE_DOCENTE)
def panel_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    context = {
        'usuario': usuario,
        'cursos': cursos,
        'total_cursos': cursos.count()
    }
    return render(request, 'panel_docente.html', context)