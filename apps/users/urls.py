from django.urls import path
from . import views
from .views.chat_views import chat
from .views.admin_views import crear_admin


urlpatterns = [
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sesion/', views.sesion, name='sesion'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('chat/', chat, name='chat'),
    path('crear-admin/', crear_admin, name='crear_admin'),
    path('agregar_usuario_ajax/', views.agregar_usuario_ajax, name='agregar_usuario_ajax'),
]
