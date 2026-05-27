from django.urls import path
from apps.users.views.docentes.index_docente import index_docente
from apps.users.views.docentes.perfil_docente import perfil_docente
from apps.users.views.docentes.consultar_progreso import consultar_progreso
from apps.users.views.docentes.cursos_promociones import cursos_promociones
from apps.users.views.docentes.Foros import foros
from apps.users.views.docentes.promociones_docente import promociones_docente
from apps.users.views.docentes.panel_docente import panel_docente
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
    path('foros/', foros, name='foros'),            #Foros
    path('promociones-docente/', promociones_docente, name='promociones_docente'),     #Promociones conexion con fabiola y norma
    path('promociones-vertical/', promociones_vertical, name='promociones_vertical'),
    path('promociones-horizontal/', promociones_horizontal, name='promociones_horizontal'),
    path('ajax/datos/', datos_docente_ajax, name='datos_docente_ajax'),
    
]
