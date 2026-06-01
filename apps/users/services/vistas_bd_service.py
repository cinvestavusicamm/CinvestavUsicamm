"""
Servicio legado de vistas - mantiene compatibilidad hacia atrás
Funcionalidad refactorizada a dashboard_builders.py

DEPRECATED: Usar directamente los builders en dashboard_builders.py
"""
from apps.users.services.dashboard_builders import (
    VistasBdService as NewVistasBdService,
    EvaluadorContextBuilder,
    GeneradorContextBuilder,
    DocenteContextBuilder,
    AdminContextBuilder,
    DashboardContextBuilder,
)


# Re-exportar para mantener compatibilidad
class VistasBdService(NewVistasBdService):
    """Clase legada que re-exporta funcionalidad refactorizada"""
    pass


__all__ = [
    'VistasBdService',
    'EvaluadorContextBuilder',
    'GeneradorContextBuilder',
    'DocenteContextBuilder',
    'AdminContextBuilder',
    'DashboardContextBuilder',
]
