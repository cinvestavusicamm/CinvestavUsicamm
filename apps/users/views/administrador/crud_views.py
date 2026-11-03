from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from apps.users.config.constants import (
    ESTADO_BORRADOR,
    ESTADOS_CURSO,
    ROLE_ADMIN,
    ROLE_DOCENTE,
    ROLE_EVALUADOR,
    ROLE_GENERADOR,
)
from apps.users.models import Curso, Rol, Usuario
from apps.users.services.curso_service import CursoInvalido, CursoService
from apps.users.services.permisos import requiere_rol
from .admin_views import _registrar_bitacora

ROLES_SISTEMA = (ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR)


def _entero_o_none(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _docentes_disponibles():
    return (
        Usuario.objects
        .filter(activo=True)
        .select_related('rol')
        .order_by('nombre', 'apellido_paterno')
    )


def _form_data_curso(curso=None, post=None):
    if post is not None:
        return {
            'titulo': post.get('titulo', '').strip(),
            'descripcion': post.get('descripcion', '').strip(),
            'docente_id': post.get('docente', '').strip(),
            'estado': post.get('estado', ESTADO_BORRADOR).strip(),
            'generado_con_ia': post.get('generado_con_ia') == 'on',
        }

    if curso is not None:
        return {
            'titulo': curso.titulo,
            'descripcion': curso.descripcion or '',
            'docente_id': str(curso.docente_id),
            'estado': curso.estado or ESTADO_BORRADOR,
            'generado_con_ia': curso.generado_con_ia,
        }

    return {
        'titulo': '',
        'descripcion': '',
        'docente_id': '',
        'estado': ESTADO_BORRADOR,
        'generado_con_ia': False,
    }


def _validar_nombre_rol(nombre, rol_id=None):
    if not nombre:
        return 'El nombre del rol es obligatorio'
    limite = Rol._meta.get_field('nombre_rol').max_length
    if len(nombre) > limite:
        return f'El nombre del rol no puede pasar de {limite} caracteres'

    existentes = Rol.objects.filter(nombre_rol__iexact=nombre)
    if rol_id is not None:
        existentes = existentes.exclude(id_rol=rol_id)
    if existentes.exists():
        return 'Ya existe un rol con ese nombre'
    return None


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET"])
def cursos_admin(request):
    busqueda = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()

    cursos = Curso.objects.select_related('docente').order_by('-fecha_creacion')

    if busqueda:
        cursos = cursos.filter(
            Q(titulo__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(docente__nombre__icontains=busqueda)
            | Q(docente__apellido_paterno__icontains=busqueda)
            | Q(docente__correo__icontains=busqueda)
        )
    if estado in ESTADOS_CURSO:
        cursos = cursos.filter(estado=estado)

    page_obj = Paginator(cursos, 15).get_page(request.GET.get('page'))

    return render(request, 'administrador/cursos.html', {
        'page_obj': page_obj,
        'q': busqueda,
        'estado_seleccionado': estado,
        'estados': ESTADOS_CURSO,
        'seccion': 'cursos',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET", "POST"])
def curso_crear(request):
    if request.method == 'POST':
        form_data = _form_data_curso(post=request.POST)
        docente_id = _entero_o_none(form_data['docente_id'])

        if docente_id is None:
            messages.error(request, 'Selecciona un docente válido')
        else:
            try:
                curso = CursoService.crear_curso(
                    titulo=form_data['titulo'],
                    descripcion=form_data['descripcion'] or None,
                    docente_id=docente_id,
                    estado=form_data['estado'],
                    generado_con_ia=form_data['generado_con_ia'],
                )
            except CursoInvalido as exc:
                messages.error(request, exc.mensaje)
            else:
                _registrar_bitacora(
                    request,
                    'CURSO_CREADO',
                    f'Creó el curso {curso.id_curso}',
                    {'curso': curso.id_curso},
                )
                messages.success(request, 'Curso creado correctamente')
                return redirect('administrador:cursos')
    else:
        form_data = _form_data_curso()

    return render(request, 'administrador/curso_form.html', {
        'curso': None,
        'form_data': form_data,
        'docentes': _docentes_disponibles(),
        'estados': ESTADOS_CURSO,
        'seccion': 'cursos',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET", "POST"])
def curso_editar(request, id):
    curso = get_object_or_404(Curso, id_curso=id)

    if request.method == 'POST':
        form_data = _form_data_curso(post=request.POST)
        docente_id = _entero_o_none(form_data['docente_id'])

        if docente_id is None:
            messages.error(request, 'Selecciona un docente válido')
        else:
            try:
                curso = CursoService.actualizar_curso(
                    curso.id_curso,
                    titulo=form_data['titulo'],
                    descripcion=form_data['descripcion'],
                    estado=form_data['estado'],
                    docente_id=docente_id,
                    generado_con_ia=form_data['generado_con_ia'],
                )
            except CursoInvalido as exc:
                messages.error(request, exc.mensaje)
            else:
                _registrar_bitacora(
                    request,
                    'CURSO_ACTUALIZADO',
                    f'Actualizó el curso {curso.id_curso}',
                    {'curso': curso.id_curso},
                )
                messages.success(request, 'Curso actualizado correctamente')
                return redirect('administrador:cursos')
    else:
        form_data = _form_data_curso(curso=curso)

    return render(request, 'administrador/curso_form.html', {
        'curso': curso,
        'form_data': form_data,
        'docentes': _docentes_disponibles(),
        'estados': ESTADOS_CURSO,
        'seccion': 'cursos',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_POST
def curso_eliminar(request, id):
    curso = get_object_or_404(Curso, id_curso=id)
    curso_id = curso.id_curso
    titulo = curso.titulo

    try:
        curso.delete()
    except ProtectedError:
        messages.error(
            request,
            'No se puede eliminar el curso porque tiene registros asociados.',
        )
    else:
        _registrar_bitacora(
            request,
            'CURSO_ELIMINADO',
            f'Eliminó el curso {curso_id}',
            {'curso': curso_id},
        )
        messages.success(request, f'Curso "{titulo}" eliminado correctamente')

    return redirect('administrador:cursos')


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET"])
def roles_admin(request):
    roles = list(
        Rol.objects
        .annotate(total_usuarios=Count('usuario'))
        .order_by('nombre_rol')
    )
    for rol in roles:
        rol.es_sistema = rol.nombre_rol in ROLES_SISTEMA

    return render(request, 'administrador/roles.html', {
        'roles': roles,
        'seccion': 'roles',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET", "POST"])
def rol_crear(request):
    form_data = {'nombre_rol': ''}

    if request.method == 'POST':
        form_data['nombre_rol'] = request.POST.get('nombre_rol', '').strip().upper()
        error = _validar_nombre_rol(form_data['nombre_rol'])

        if error:
            messages.error(request, error)
        else:
            rol = Rol.objects.create(nombre_rol=form_data['nombre_rol'])
            _registrar_bitacora(
                request,
                'ROL_CREADO',
                f'Creó el rol {rol.id_rol}',
                {'rol': rol.id_rol},
            )
            messages.success(request, 'Rol creado correctamente')
            return redirect('administrador:roles')

    return render(request, 'administrador/rol_form.html', {
        'rol': None,
        'form_data': form_data,
        'es_sistema': False,
        'seccion': 'roles',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_http_methods(["GET", "POST"])
def rol_editar(request, id):
    rol = get_object_or_404(Rol, id_rol=id)
    es_sistema = rol.nombre_rol in ROLES_SISTEMA
    form_data = {'nombre_rol': rol.nombre_rol}

    if request.method == 'POST':
        if es_sistema:
            messages.error(request, 'Los roles del sistema no se pueden renombrar.')
        else:
            form_data['nombre_rol'] = request.POST.get('nombre_rol', '').strip().upper()
            error = _validar_nombre_rol(form_data['nombre_rol'], rol.id_rol)

            if error:
                messages.error(request, error)
            else:
                rol.nombre_rol = form_data['nombre_rol']
                rol.save(update_fields=['nombre_rol'])
                _registrar_bitacora(
                    request,
                    'ROL_ACTUALIZADO',
                    f'Actualizó el rol {rol.id_rol}',
                    {'rol': rol.id_rol},
                )
                messages.success(request, 'Rol actualizado correctamente')
                return redirect('administrador:roles')

    return render(request, 'administrador/rol_form.html', {
        'rol': rol,
        'form_data': form_data,
        'es_sistema': es_sistema,
        'seccion': 'roles',
    })


@never_cache
@requiere_rol(ROLE_ADMIN)
@require_POST
def rol_eliminar(request, id):
    rol = get_object_or_404(Rol, id_rol=id)
    rol_id = rol.id_rol
    nombre = rol.nombre_rol

    if nombre in ROLES_SISTEMA:
        messages.error(request, 'No se puede eliminar un rol del sistema.')
    elif Usuario.objects.filter(rol=rol).exists():
        messages.error(
            request,
            'No se puede eliminar un rol que tiene usuarios asignados.',
        )
    else:
        rol.delete()
        _registrar_bitacora(
            request,
            'ROL_ELIMINADO',
            f'Eliminó el rol {rol_id}',
            {'rol': rol_id},
        )
        messages.success(request, f'Rol "{nombre}" eliminado correctamente')

    return redirect('administrador:roles')
