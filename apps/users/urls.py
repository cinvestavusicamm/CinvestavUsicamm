from django.urls import path
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .views.admin_views import panel_admin
from .views.admin_users_views import crear_admin, agregar_usuario_ajax, obtener_usuario_ajax, editar_usuario_ajax
from .views.chat_views import chat
from .views.agent_ajax import agente_ajax

urlpatterns = [
    path('', dashboard, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('sesion/', sesion, name='sesion'),
    path('registro/', registro, name='registro'),
    path('logout/', cerrar_sesion, name='logout'),

    path('panel-admin/', panel_admin, name='panel_admin'),

    path('crear-admin/', crear_admin, name='crear_admin'),
    path('agregar_usuario_ajax/', agregar_usuario_ajax, name='agregar_usuario_ajax'),
    path('usuario/<int:id>/obtener/', obtener_usuario_ajax, name='obtener_usuario_ajax'),
    path('usuario/<int:id>/editar/', editar_usuario_ajax, name='editar_usuario_ajax'),

    path('chat/', chat, name='chat'),
    path('agente-ajax/', agente_ajax, name='agente_ajax'),
]
