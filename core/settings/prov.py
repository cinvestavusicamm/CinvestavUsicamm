from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import DATABASE_URL, INTERNAL_SERVICE_KEY

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

# La clave del microservicio de IA tambien es obligatoria aqui, y se comprueba
# al arrancar en vez de al usar el endpoint. Si falta, Django seguiria
# arrancando y sirviendo paginas, y el fallo apareceria como un 500 en el
# chatbot mucho despues de un despliegue que en realidad salio bien. Con el
# valor por defecto escrito en el codigo -- como estaba antes -- el despliegue
# no fallaba nunca, que es justo lo que hay que evitar: la clave era la misma
# para todos los entornos y no se podia rotar sin tocar el repositorio.
if not INTERNAL_SERVICE_KEY:
    raise ImproperlyConfigured(
        'INTERNAL_SERVICE_KEY es obligatoria en produccion. Definela en el '
        'entorno con el mismo valor que lea el microservicio de IA, para que '
        'la cabecera X-Internal-Service-Key coincida; no hay valor por defecto '
        'a proposito.'
    )
