from django.urls import path
from apps.users.views.generador_cursos.cursos import (cursos,crear_curso_generador,actualizar_curso_generador,eliminar_curso_generador,obtener_curso_generador)
from apps.users.views.generador_cursos.estadisticas_cursos import (estadisticas_cursos,obtener_estadisticas_api)
from apps.users.views.generador_cursos.generador_de_cursos import (generador_de_cursos,guardar_curso_generado)
from apps.users.views.generador_cursos.index_generador import (index_generador,crear_curso_index)
from apps.users.views.generador_cursos.perfil_generador import (perfil_generador,actualizar_perfil_generador)
from apps.users.api.cursos import crear_curso_api, actualizar_curso_api, eliminar_curso_api
from apps.users.api.roles import datos_generador_ajax

app_name = 'generador_cursos'

urlpatterns = [
    path('dashboard/', index_generador, name='index_generador'),
    path('cursos/', cursos, name='cursos'),
    path('estadisticas-cursos/', estadisticas_cursos, name='estadisticas_cursos'),
    path('generador_de_cursos/', generador_de_cursos, name='generador_de_cursos'),
    path('generador_de_cursos/<int:curso_id>/', generador_de_cursos, name='generador_de_cursos_editar'),
    path('perfil-generador/', perfil_generador, name='perfil_generador'),
    path('ajax/datos/', datos_generador_ajax, name='datos_generador_ajax'),

    # API endpoints que manejan contenido JSON 
    path('api/crear-curso-generador/', crear_curso_generador, name='crear_curso_generador'),
    path('api/actualizar-curso-generador/<int:curso_id>/', actualizar_curso_generador, name='actualizar_curso_generador'),
    path('api/eliminar-curso-generador/<int:curso_id>/', eliminar_curso_generador, name='eliminar_curso_generador'),
    path('api/obtener-curso/<int:curso_id>/', obtener_curso_generador, name='obtener_curso_generador'),
    path('api/guardar-curso-generado/', guardar_curso_generado, name='guardar_curso_generado'),

    # Otros endpoints (
    path('api/crear/', crear_curso_api, name='crear_curso_api'),
    path('api/actualizar/<int:curso_id>/', actualizar_curso_api, name='actualizar_curso_api'),
    path('api/eliminar/<int:curso_id>/', eliminar_curso_api, name='eliminar_curso_api'),
    path('api/crear-curso-index/', crear_curso_index, name='crear_curso_index'),
    path('api/obtener-estadisticas/', obtener_estadisticas_api, name='obtener_estadisticas_api'),
    path('api/actualizar-perfil-generador/', actualizar_perfil_generador, name='actualizar_perfil_generador'),
]