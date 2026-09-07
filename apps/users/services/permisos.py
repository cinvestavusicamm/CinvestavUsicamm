from functools import wraps
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR


def requiere_rol(*roles_permitidos):

    def decorator(view_func):
        @wraps(view_func)
        @never_cache
        def wrapper(request, *args, **kwargs):
            if not request.session.get('usuario_id'):
                return redirect('sesion')

            rol_usuario = request.session.get('usuario_rol')
            if rol_usuario not in roles_permitidos:
                return redirect('sesion')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

