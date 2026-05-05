from django.shortcuts import render
from apps.users.services.permisos import requiere_rol
from apps.users.constants import ROLE_DOCENTE
from apps.users.models import Usuario
from apps.users.services.foro_service import ForoService
from apps.users.services.curso_service import CursoService

@requiere_rol(ROLE_DOCENTE)
def foros(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id_usuario=usuario_id)
    cursos = CursoService.obtener_cursos_docente(usuario_id)
    
    foro_items = []
    for curso in cursos:
        foro_items.append({
            'curso': curso,
            'foros': ForoService.obtener_foros_curso(curso.id_curso),
        })
    
    context = {
        'usuario': usuario,
        'cursos': cursos,
        'foro_items': foro_items,
    }
    return render(request, 'docente/Foros.html', context)
