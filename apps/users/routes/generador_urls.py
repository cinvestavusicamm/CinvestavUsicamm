from django.urls import path
from apps.users.views.generador_cursos.cursos import cursos
from apps.users.views.generador_cursos.estadisticas_cursos import estadisticas_cursos
from apps.users.views.generador_cursos.generador_de_cursos import generador_de_cursos
from apps.users.views.generador_cursos.index_generador import index_generador
from apps.users.views.generador_cursos.perfil_generador import perfil_generador
from apps.users.api.cursos import crear_curso_api, actualizar_curso_api
from apps.users.api.roles import datos_generador_ajax

app_name = 'generador_cursos'

urlpatterns = [
    path('dashboard/', index_generador, name='index_generador'),
    path('cursos/', cursos, name='cursos'),
    path('estadisticas-cursos/', estadisticas_cursos, name='estadisticas_cursos'),
    path('generador_de_cursos/', generador_de_cursos, name='generador_de_cursos'),
    path('perfil-generador/', perfil_generador, name='perfil_generador'),
    path('ajax/datos/', datos_generador_ajax, name='datos_generador_ajax'),
    # API endpoints
    path('api/crear/', crear_curso_api, name='crear_curso_api'),
    path('api/actualizar/<int:curso_id>/', actualizar_curso_api, name='actualizar_curso_api'),
]
