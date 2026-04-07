from django.shortcuts import render, redirect
from ..models import Institucion, Usuario, Rol
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

@never_cache
def panel_admin(request):
    if not request.session.get('usuario_id'):
        return redirect('sesion')

    admins = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol='Administrador')

    docentes = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol='Docente')

    instituciones = Institucion.objects.all()
    roles = Rol.objects.all()

    total_registros = Usuario.objects.count()
    activos = Usuario.objects.filter(activo=True).count()
    en_revision = Usuario.objects.filter(activo=False).count()

    return render(request, 'paneladm.html', {
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
