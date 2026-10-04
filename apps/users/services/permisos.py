from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.views.decorators.cache import never_cache
from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR


def _pide_json(request):
    """True si el cliente espera JSON en lugar de una pagina HTML."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept', '')
    return 'application/json' in accept


def requiere_rol(*roles_permitidos):

    def decorator(view_func):
        @wraps(view_func)
        @never_cache
        def wrapper(request, *args, **kwargs):
            # Sin sesion no hay nada que autorizar: al login.
            if not request.session.get('usuario_id'):
                return redirect('sesion')

            # Con sesion pero sin el rol, no es un fallo de autenticacion sino de
            # autorizacion: se responde 403 y no se redirige, para no hidear el
            # motivo y para no devolver HTML donde el AJAX espera JSON.
            rol_usuario = request.session.get('usuario_rol')
            if rol_usuario not in roles_permitidos:
                if _pide_json(request):
                    from apps.users.infrastructure.api_response import respuesta_error
                    return respuesta_error(
                        request,
                        'No tiene permisos para realizar esta accion',
                        status=403,
                    )
                return HttpResponseForbidden(
                    'No tiene permisos para acceder a esta pagina.'
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator