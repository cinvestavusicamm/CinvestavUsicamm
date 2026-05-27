from django.urls import path, include
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .views.admin_views import panel_admin
from .views.admin_users_views import crear_admin, agregar_usuario_ajax, editar_usuario_ajax, toggle_usuario, obtener_usuario_ajax
from .views.agent_ajax import agente_ajax
from .views.db_schema_views import listar_tablas_bd
from apps.users.views.docente_ajax import docente_ajax
from apps.users.views.evaluador_ajax import evaluador_ajax
from apps.users.views.generador_ajax import generador_ajax

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


]
