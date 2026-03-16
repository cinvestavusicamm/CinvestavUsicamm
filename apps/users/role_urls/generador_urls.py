from django.urls import path
from apps.users.views.Generador_cursos.cursos import cursos
from apps.users.views.Generador_cursos.estadisticas_cursos import estadisticas_cursos
from apps.users.views.Generador_cursos.generador_de_cursos import generador_de_cursos
from apps.users.views.Generador_cursos.index_generador import index_generador
from apps.users.views.Generador_cursos.perfil_generador import perfil_generador

app_name = 'generador_cursos'

urlpatterns = [
    path('dashboard/', index_generador, name='index_generador'),
    path('cursos/', cursos, name='cursos'),
    path('estadisticas-cursos/', estadisticas_cursos, name='estadisticas_cursos'),
    path('generador_de_cursos/', generador_de_cursos, name='generador_de_cursos'),
    path('perfil-generador/', perfil_generador, name='perfil_generador'),
]
