from django.urls import path
from apps.users.views.docentes.index_docente import index_docente
from apps.users.views.docentes.perfil_docente import perfil_docente, actualizar_perfil_docente, actualizar_contrasena_docente
from apps.users.views.docentes.consultar_progreso import consultar_progreso, actualizar_progreso_docente, ver_certificado
from apps.users.views.docentes.cursos_promociones import cursos_promociones
from apps.users.views.docentes.Foros import foros, crear_foro_docente, actualizar_foro_docente, eliminar_foro_docente, crear_post_docente, actualizar_post_docente, eliminar_post_docente
from apps.users.views.docentes.promociones_docente import promociones_docente
from apps.users.views.docentes.panel_docente import panel_docente, crear_curso_panel, actualizar_curso_panel, eliminar_curso_panel, crear_foro_panel, crear_post_panel
from apps.users.views.docentes.vertical import promociones_vertical
from apps.users.views.docentes.horizontal import promociones_horizontal
from apps.users.api.roles import datos_docente_ajax

app_name ='Docente'

urlpatterns = [
    path('index/', index_docente, name='index_docente'),
    path('perfil/', perfil_docente, name='perfil'),     #Consultar perfil propio
    path('panel-docente/', panel_docente, name= 'panel_docente'),
    path('cursos-promociones/', cursos_promociones, name='cursos_promociones'),     #Promocion
    path('consultar-progreso/', consultar_progreso, name='consultar_progreso'),     #Consultar progreso del docente
    path('ver-certificado/<int:curso_id>/', ver_certificado, name='ver_certificado'),     #Ver certificado de curso
    path('foros/', foros, name='foros'),            #Foros
    path('promociones-docente/', promociones_docente, name='promociones_docente'),     #Promociones conexion con fabiola y norma
    path('promociones-vertical/', promociones_vertical, name='promociones_vertical'),
    path('promociones-horizontal/', promociones_horizontal, name='promociones_horizontal'),
    path('ajax/datos/', datos_docente_ajax, name='datos_docente_ajax'),
    
    # API endpoints para CRUD
    path('api/crear-curso/', crear_curso_panel, name='crear_curso_panel'),
    path('api/actualizar-curso/<int:curso_id>/', actualizar_curso_panel, name='actualizar_curso_panel'),
    path('api/eliminar-curso/<int:curso_id>/', eliminar_curso_panel, name='eliminar_curso_panel'),
    path('api/crear-foro/', crear_foro_panel, name='crear_foro_panel'),
    path('api/crear-post/', crear_post_panel, name='crear_post_panel'),
    path('api/actualizar-perfil/', actualizar_perfil_docente, name='actualizar_perfil_docente'),
    path('api/actualizar-contrasena/', actualizar_contrasena_docente, name='actualizar_contrasena_docente'),
    path('api/actualizar-progreso/', actualizar_progreso_docente, name='actualizar_progreso_docente'),
    path('api/crear-foro-docente/', crear_foro_docente, name='crear_foro_docente'),
    path('api/actualizar-foro/<int:foro_id>/', actualizar_foro_docente, name='actualizar_foro_docente'),
    path('api/eliminar-foro/<int:foro_id>/', eliminar_foro_docente, name='eliminar_foro_docente'),
    path('api/crear-post-docente/', crear_post_docente, name='crear_post_docente'),
    path('api/actualizar-post/<int:post_id>/', actualizar_post_docente, name='actualizar_post_docente'),
    path('api/eliminar-post/<int:post_id>/', eliminar_post_docente, name='eliminar_post_docente'),
]
