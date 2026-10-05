from django.urls import path, include
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .api.agente import agente_ajax
from .api.admin import listar_tablas_bd
from .api.health import health_check
from .api.foros_api import api_listar_foros
from .views.docente_ajax import docente_ajax
from .views.evaluador_ajax import evaluador_ajax
from .views.generador_ajax import generador_ajax


urlpatterns = [
    path('', dashboard, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('sesion/', sesion, name='sesion'),
    path('registro/', registro, name='registro'),
    path('logout/', cerrar_sesion, name='logout'),
    path('foros/', sesion, name='foros'),

    path('agente-ajax/', agente_ajax, name='agente_ajax'),

    path('administrador/', include('apps.users.routes.administrador_urls')),
    path('evaluador/', include('apps.users.routes.evaluador_urls')),
    path('generador/', include('apps.users.routes.generador_urls')),
    path('docente/', include('apps.users.routes.docentes_urls')),
    path('docente/ajax/', docente_ajax, name='docente_ajax'),
    path('evaluador/ajax/', evaluador_ajax, name='evaluador_ajax'),
    path('generador/ajax/', generador_ajax, name='generador_ajax'),

    # API endpoints para ms_orchestrator
    path('health/', health_check, name='health_check'),

    # Las rutas /api/cursos/* se retiraron. No las consumia ni la interfaz ni
    # ms_orchestrator, y api_listar_cursos respondia sin autenticacion con
    # Curso.objects.all().values(), es decir todos los cursos y su
    # contenido_json a cualquiera que preguntara. El listado de un generador
    # sigue en /generador/api/cursos/ y en /generador/api/obtener-curso/.
    # Ver PLAN.md, DEUDA-10.

    # API endpoints para foros
    path('api/foros/listar/', api_listar_foros, name='api_listar_foros'),

]
