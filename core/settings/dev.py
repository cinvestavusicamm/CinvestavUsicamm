from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlparse

from .base import *  # noqa: F401,F403
from .base import DATABASE_URL

DEBUG = False

# En desarrollo la base debe ser local: el Postgres del docker-compose o un
# SQLite. Si el DATABASE_URL resuelto apunta a un host remoto casi siempre es un
# olvido del .env local en vez de una decision, y developiendo contra una base
# de otra persona termina en datos perdidos.
#
# Para trabajar contra un host remoto a proposito:
#   ALLOW_REMOTE_DB=1 python manage.py ...
_HOST = urlparse(DATABASE_URL).hostname if DATABASE_URL else None
_ES_LOCAL = _HOST in (None, '', 'localhost', '127.0.0.1', '::1', 'db', 'postgres')

if not _ES_LOCAL and not config('ALLOW_REMOTE_DB', default=False, cast=bool):  # noqa: F405
    raise ImproperlyConfigured(
        f'DATABASE_URL apunta al host remoto {_HOST!r} y el desarrollo esta '
        'configurado para usar una base local. O se deja el DATABASE_URL vacio '
        'para trabajar con el SQLite local, o se ajusta a la del '
        'docker-compose, o si el acceso remoto es deliberado se exporta '
        'ALLOW_REMOTE_DB=1.'
    )