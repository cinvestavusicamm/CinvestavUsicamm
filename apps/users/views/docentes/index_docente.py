from django.shortcuts import redirect
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_DOCENTE


@requiere_rol(ROLE_DOCENTE)
def index_docente(request):
    """Redirige al panel del docente.

    Antes renderizaba 'docente/index_docente.html', una plantilla que no
    existe en el repositorio: la ruta devolvia 500 con TemplateDoesNotExist
    para cualquier DOCENTE que la abriera. El contexto que armaba aqui es
    identico al de panel_docente, asi que la ruta pasa a redirigir alli.
    """
    return redirect('Docente:panel_docente')