from django.urls import path
from apps.users.views.docente.dashboard import dashboard


app_name ='Docentes'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
]