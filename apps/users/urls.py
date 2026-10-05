from django.urls import path, include
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .api.agente import agente_ajax
from .api.admin import listar_tablas_bd
from .api.health import health_check
from .api.cursos_api import api_listar_cursos, api_crear_curso, api_actualizar_curso
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
    
    # API endpoints para cursos
    path('api/cursos/listar/', api_listar_cursos, name='api_listar_cursos'),
    path('api/cursos/crear/', api_crear_curso, name='api_crear_curso'),
    path('api/cursos/actualizar/<int:curso_id>/', api_actualizar_curso, name='api_actualizar_curso'),
    
    # API endpoints para foros
    path('api/foros/listar/', api_listar_foros, name='api_listar_foros'),

]
