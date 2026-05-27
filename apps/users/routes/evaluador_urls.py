from django.urls import path
from apps.users.views.evaluador.dashboard import dashboard
from apps.users.views.evaluador.chat import chat
from apps.users.views.evaluador.banco_preguntas import banco_preguntas
from apps.users.views.evaluador.evaluaciones import evaluaciones
from apps.users.views.evaluador.validaciones import validaciones
from apps.users.views.evaluador.calendario import calendario
from apps.users.views.evaluador.reportes import reportes
from apps.users.views.evaluador.perfil import perfil
from apps.users.views.evaluador.configuracion import configuracion
from apps.users.api.roles import datos_evaluador_ajax

app_name = 'evaluador'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('chat/', chat, name='chat'),
    path('banco-preguntas/', banco_preguntas, name='banco_preguntas'),
    path('evaluaciones/', evaluaciones, name='evaluaciones'),
    path('validaciones/', validaciones, name='validaciones'),
    path('calendario/', calendario, name='calendario'),
    path('reportes/', reportes, name='reportes'),
    path('perfil/', perfil, name='perfil'),
    path('configuracion/', configuracion, name='configuracion'),
    path('ajax/datos/', datos_evaluador_ajax, name='datos_evaluador_ajax'),
]
