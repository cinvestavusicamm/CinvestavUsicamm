from django.urls import path, include
from .views.auth_views import sesion, registro, cerrar_sesion
from .views.dashboard_views import dashboard
from .views.admin_views import panel_admin
from .views.admin_users_views import crear_admin, agregar_usuario_ajax, obtener_usuario_ajax, editar_usuario_ajax
from .views.chat_views import chat
from .views.agent_ajax import agente_ajax

from .views.docente_views import panel_docente, index_docente, perfil_docente
from .views.evaluador_views import (
    dashboard_evaluador, banco_preguntas, validaciones, 
    chat_ia_evaluador, evaluaciones, calendario_evaluador, 
    reportes_evaluador, generador_ia_evaluador
)
from .views.generador_views import (
    index_generador, mis_cursos, perfil_generador, estadisticas_cursos
)
from .views.extra_views import prueba, foros, consultar_progreso, cursos_promociones, rutas_promocion

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

    path('evaluador/', include('apps.users.role_urls.evaluador_urls')),

    path('panel-docente/', panel_docente, name='panel_docente'),
    path('index-docente/', index_docente, name='index_docente'),
    path('perfil-docente/', perfil_docente, name='perfil_docente'),

    path('generador/', index_generador, name='index_generador'),
    path('generador/mis-cursos/', mis_cursos, name='mis_cursos'),
    path('generador/perfil/', perfil_generador, name='perfil_generador'),
    path('generador/estadisticas/', estadisticas_cursos, name='estadisticas_cursos'),
    
    path('foros/', foros, name='foros'),
    path('consultar-progreso/', consultar_progreso, name='consultar_progreso'),
    path('cursos-promociones/', cursos_promociones, name='cursos_promociones'),
    path('rutas-promocion/', rutas_promocion, name='rutas_promocion'),

]