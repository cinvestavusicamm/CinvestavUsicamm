"""
Decoradores para control de permisos, validación y manejo de errores
"""
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from apps.users.config.constants import ROLE_ADMINISTRADOR, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
import json


def require_role(*roles):
    """
    Decorator que verifica si el usuario tiene uno de los roles requeridos
    
    Usage:
        @require_role('Administrador')
        @require_role('Administrador', 'Docente')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'No autenticado'}, status=401)
                return redirect('login')
            
            # Obtener rol del usuario
            user_role = getattr(request.user, 'rol', None)
            if user_role and user_role.nombre in roles:
                return view_func(request, *args, **kwargs)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Acceso denegado'}, status=403)
            return redirect('login')
        return wrapper
    return decorator


def require_auth(view_func):
    """
    Decorator que verifica autenticación básica
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'No autenticado'}, status=401)
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def validate_json(*required_fields):
    """
    Decorator que valida que el request sea JSON y tenga campos requeridos
    
    Usage:
        @validate_json('titulo', 'descripcion')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON inválido'}, status=400)
            
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }, status=400)
            
            request.json_data = data
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def api_view(allowed_methods=None):
    """
    Decorator para API endpoints
    
    Usage:
        @api_view(['GET', 'POST'])
    """
    allowed_methods = allowed_methods or ['GET']
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed_methods:
                return JsonResponse({
                    'error': f'Método {request.method} no permitido'
                }, status=405)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def handle_exceptions(view_func):
    """
    Decorator que maneja excepciones generales y retorna JSON
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'type': type(e).__name__
            }, status=500)
    return wrapper
