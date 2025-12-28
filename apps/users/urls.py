from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('chat/', views.chat, name='chat'),
    path('prueba/', views.prueba, name='prueba'),
]
