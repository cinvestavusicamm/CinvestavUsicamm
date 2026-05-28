from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Institucion, Usuario, Rol
from django.views.decorators.cache import never_cache
from apps.users.constants import ROLE_ADMIN, ROLE_DOCENTE
from apps.users.services.permisos import requiere_rol

@never_cache
@requiere_rol(ROLE_ADMIN)
def panel_admin(request):
    
    admins_all = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol=ROLE_ADMIN).order_by('id_usuario')
    
    docentes_all = Usuario.objects.select_related('rol', 'institucion') \
        .filter(rol__nombre_rol=ROLE_DOCENTE).order_by('id_usuario')
    
    paginator_admins = Paginator(admins_all, 8)
    paginator_docentes = Paginator(docentes_all, 8)
    
    # Obtener número de página de los parámetros GET
    page_admins = request.GET.get('page_admins', 1)
    page_docentes = request.GET.get('page_docentes', 1)
    
    try:
        admins = paginator_admins.page(page_admins)
    except PageNotAnInteger:
        admins = paginator_admins.page(1)
    except EmptyPage:
        admins = paginator_admins.page(paginator_admins.num_pages)
    
    try:
        docentes = paginator_docentes.page(page_docentes)
    except PageNotAnInteger:
        docentes = paginator_docentes.page(1)
    except EmptyPage:
        docentes = paginator_docentes.page(paginator_docentes.num_pages)
    
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