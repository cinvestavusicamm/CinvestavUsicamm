from django.contrib import admin
from django.urls import path, include
from utils import error_handlers

handler400= error_handlers.error_400
handler403 = error_handlers.error_403
handler404 = error_handlers.error_404
handler500 = error_handlers.error_500

CSRF_FAILURE_VIEW = 'utils.error_handlers.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
]
