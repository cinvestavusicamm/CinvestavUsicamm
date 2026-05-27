from django.urls import path, include
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .views.administrador.admin_views import panel_admin
from .views.administrador.admin_users_views import crear_admin
from .api.usuarios import agregar_usuario_ajax, editar_usuario_ajax, toggle_usuario, obtener_usuario_ajax
from .api.agente import agente_ajax
from .api.admin import listar_tablas_bd
from .api.health import health_check
from .api.usuarios_api import api_get_usuario, api_create_usuario, api_update_usuario, api_toggle_usuario
from .api.cursos_api import api_listar_cursos, api_crear_curso, api_actualizar_curso
from .api.foros_api import api_listar_foros


urlpatterns = [
    path('', dashboard, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('sesion/', sesion, name='sesion'),
    path('registro/', registro, name='registro'),
    path('logout/', cerrar_sesion, name='logout'),
    path('foros/', sesion, name='foros'),

    path('agente-ajax/', agente_ajax, name='agente_ajax'),

    path('evaluador/', include('apps.users.routes.evaluador_urls')),
    path('generador/', include('apps.users.routes.generador_urls')),
    path('docente/', include('apps.users.routes.docentes_urls')),
    path('administrador/', include('apps.users.routes.admin_urls')),

    # API endpoints para ms_orchestrator
    path('health/', health_check, name='health_check'),
    
    # API endpoints para usuarios
    path('api/usuarios/<int:usuario_id>/', api_get_usuario, name='api_get_usuario'),
    path('api/usuarios/agregar/', api_create_usuario, name='api_create_usuario'),
    path('api/usuarios/editar/<int:usuario_id>/', api_update_usuario, name='api_update_usuario'),
    path('api/usuarios/toggle/<int:usuario_id>/', api_toggle_usuario, name='api_toggle_usuario'),
    
    # API endpoints para cursos
    path('api/cursos/listar/', api_listar_cursos, name='api_listar_cursos'),
    path('api/cursos/crear/', api_crear_curso, name='api_crear_curso'),
    path('api/cursos/actualizar/<int:curso_id>/', api_actualizar_curso, name='api_actualizar_curso'),
    
    # API endpoints para foros
    path('api/foros/listar/', api_listar_foros, name='api_listar_foros'),

]
