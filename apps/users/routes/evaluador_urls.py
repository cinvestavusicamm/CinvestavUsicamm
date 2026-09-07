from django.urls import path
from apps.users.views.evaluador.dashboard import dashboard
from apps.users.views.evaluador.chat import chat
from apps.users.views.evaluador.banco_preguntas import banco_preguntas
from apps.users.views.evaluador.evaluaciones import evaluaciones
from apps.users.views.evaluador.validaciones import validaciones, aprobar_pregunta, rechazar_pregunta, enviar_revision_pregunta
from apps.users.views.evaluador.calendario import calendario, eventos_calendario_api
from apps.users.views.evaluador.reportes import reportes
from apps.users.views.evaluador.perfil import perfil
from apps.users.views.evaluador.configuracion import (
    configuracion,
    actualizar_perfil_evaluador,
    actualizar_contrasena_evaluador,
)
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
    path('api/eventos/', eventos_calendario_api, name='eventos_api'),
    path('api/actualizar-perfil/', actualizar_perfil_evaluador, name='actualizar_perfil_evaluador'),
    path('api/actualizar-contrasena/', actualizar_contrasena_evaluador, name='actualizar_contrasena_evaluador'),
    path('ajax/datos/', datos_evaluador_ajax, name='datos_evaluador_ajax'),
    
    # API endpoints para validaciones
    path('api/aprobar-pregunta/<int:pregunta_id>/', aprobar_pregunta, name='aprobar_pregunta'),
    path('api/rechazar-pregunta/<int:pregunta_id>/', rechazar_pregunta, name='rechazar_pregunta'),
    path('api/enviar-revision-pregunta/<int:pregunta_id>/', enviar_revision_pregunta, name='enviar_revision_pregunta'),
]
