from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sesion/', views.sesion, name='sesion'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
]
