from django.urls import path
from apps.users.views.administrador.admin_views import panel_admin
from apps.users.views.administrador.admin_views import crear_admin
from apps.users.api.usuarios import agregar_usuario_ajax, editar_usuario_ajax, toggle_usuario, obtener_usuario_ajax
from apps.users.views.administrador.db_schema_views import listar_tablas_bd
from apps.users.views.administrador.crud_views import (
    cursos_admin,
    curso_crear,
    curso_editar,
    curso_eliminar,
    roles_admin,
    rol_crear,
    rol_editar,
    rol_eliminar,
)

app_name = 'administrador'

urlpatterns = [
    path('panel-admin/', panel_admin, name='panel_admin'),
    path('crear-admin/', crear_admin, name='crear_admin'),
    path('agregar_usuario_ajax/', agregar_usuario_ajax, name='agregar_usuario_ajax'),
    path('usuario/<int:id>/obtener/', obtener_usuario_ajax, name='obtener_usuario_ajax'),
    path('usuario/<int:id>/editar/', editar_usuario_ajax, name='editar_usuario_ajax'),
    path('toggle-usuario/<int:id>/', toggle_usuario, name='toggle_usuario'),
    path('bd/tablas/', listar_tablas_bd, name='bd_tablas'),
    path('cursos/', cursos_admin, name='cursos'),
    path('cursos/crear/', curso_crear, name='curso_crear'),
    path('cursos/<int:id>/editar/', curso_editar, name='curso_editar'),
    path('cursos/<int:id>/eliminar/', curso_eliminar, name='curso_eliminar'),
    path('roles/', roles_admin, name='roles'),
    path('roles/crear/', rol_crear, name='rol_crear'),
    path('roles/<int:id>/editar/', rol_editar, name='rol_editar'),
    path('roles/<int:id>/eliminar/', rol_eliminar, name='rol_eliminar'),
]
