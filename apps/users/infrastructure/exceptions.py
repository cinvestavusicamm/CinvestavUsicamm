"""
Excepciones personalizadas para la aplicación
"""


class AppException(Exception):
    """Excepción base de la aplicación"""
    def __init__(self, mensaje, codigo=400, detalles=None):
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalles = detalles or {}
        super().__init__(self.mensaje)


class NotFoundException(AppException):
    """Recurso no encontrado"""
    def __init__(self, mensaje, detalles=None):
        super().__init__(mensaje, 404, detalles)


class PermissionDeniedException(AppException):
    """Acceso denegado"""
    def __init__(self, mensaje, detalles=None):
        super().__init__(mensaje, 403, detalles)


class ValidationException(AppException):
    """Error de validación"""
    def __init__(self, mensaje, detalles=None):
        super().__init__(mensaje, 400, detalles)


class ConflictException(AppException):
    """Recurso en conflicto"""
    def __init__(self, mensaje, detalles=None):
        super().__init__(mensaje, 409, detalles)


class UnauthorizedException(AppException):
    """No autenticado"""
    def __init__(self, mensaje="No autenticado", detalles=None):
        super().__init__(mensaje, 401, detalles)
