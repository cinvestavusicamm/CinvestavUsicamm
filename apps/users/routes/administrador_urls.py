from django.urls import path
from apps.users.views.admin_views import panel_admin
from apps.users.views.admin_users_views import crear_admin, agregar_usuario_ajax, editar_usuario_ajax, toggle_usuario, obtener_usuario_ajax
from apps.users.views.db_schema_views import listar_tablas_bd

app_name = 'administrador'

urlpatterns = [
    path('dashboard/', panel_admin, name='dashboard'),
    path('panel-admin/', panel_admin, name='panel_admin'),
    path('crear-admin/', crear_admin, name='crear_admin'),
    path('agregar_usuario_ajax/', agregar_usuario_ajax, name='agregar_usuario_ajax'),
    path('usuario/<int:id>/obtener/', obtener_usuario_ajax, name='obtener_usuario_ajax'),
    path('usuario/<int:id>/editar/', editar_usuario_ajax, name='editar_usuario_ajax'),
    path('toggle-usuario/<int:id>/', toggle_usuario, name='toggle_usuario'),
    path('bd/tablas/', listar_tablas_bd, name='bd_tablas'),
]
