from django.shortcuts import render
from ..models import Institucion, Usuario, Rol
from django.views.decorators.cache import never_cache
from apps.users.constants import ROLE_ADMIN, ROLE_DOCENTE
from apps.users.services.permisos import requiere_rol

@never_cache
@requiere_rol(ROLE_ADMIN)
def panel_admin(request):

    admins = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol=ROLE_ADMIN)

    docentes = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol=ROLE_DOCENTE)

    instituciones = Institucion.objects.all()
    roles = Rol.objects.all()

    total_registros = Usuario.objects.count()
    activos = Usuario.objects.filter(activo=True).count()
    en_revision = Usuario.objects.filter(activo=False).count()

    return render(request, 'administrador/paneladm.html', {
        'admins': admins,
        'docentes': docentes,
        'instituciones': instituciones,
        'roles': roles,

        'total_registros': total_registros,
        'activos': activos,
        'en_revision': en_revision,

        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
    })
