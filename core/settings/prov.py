from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import DATABASE_URL

DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'localhost', '127.0.0.1']

# En produccion la base es obligatoria y no admite fallback: si no se indica
# DATABASES no arranca. base.py dejaria caer en un SQLite local, cosa que en
# produccion seria peor que fallar, porque el deploy pareceria tener exito
# sobre una base vacia y sin datos.
if not DATABASE_URL:
    raise ImproperlyConfigured(
        'DATABASE_URL es obligatoria en produccion. Definela en el entorno o '
        'en el archivo de variables que usa decouple; no hay valor por defecto '
        'a proposito.'
    )

# Y menos encore un SQLite: en produccion se espera un Postgres de verdad.
if DATABASE_URL.startswith('sqlite'):
    raise ImproperlyConfigured(
        'DATABASE_URL apunta a SQLite, lo que no es admisible en produccion. '
        'Configura un PostgreSQL.'
    )