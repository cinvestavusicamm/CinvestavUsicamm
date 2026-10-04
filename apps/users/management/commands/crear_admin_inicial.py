import getpass
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import Institucion, Rol, Usuario
from apps.users.services.user_service import UserService
from apps.users.config.constants import ROLE_ADMIN

CURP_PATTERN = re.compile(r'^[A-Z0-9]{17,18}$')


class Command(BaseCommand):
    help = (
        "Crea el primer usuario ADMIN del sistema de forma interactiva. "
        "Sustituye al registro publico que antes permitia crear administradores "
        "sin autenticacion."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help=' correo del administrador. Si se omite, se pregunta por consola.'
        )

    def _preguntar(self, texto, default=None, oculto=False):
        while True:
            try:
                if oculto:
                    valor = getpass.getpass(f'{texto}: ')
                else:
                    valor = input(f'{texto}: ')
            except EOFError:
                raise CommandError('Entrada cancelada.')
            valor = valor.strip()
            if valor:
                return valor
            if default is not None:
                return default
            self.stdout.write(self.style.WARNING('El valor no puede quedar vacio.'))

    @transaction.atomic
    def handle(self, *args, **options):
        if Usuario.objects.filter(rol__nombre_rol=ROLE_ADMIN).exists():
            raise CommandError(
                'Ya existe al menos un ADMIN en el sistema. '
                'Para crear mas, usa el panel de administrador.'
            )

        if not Institucion.objects.exists():
            raise CommandError(
                'No hay instituciones registradas. Ejecuta primero: '
                'python manage.py create_initial_data'
            )

        try:
            rol_admin = Rol.objects.get(nombre_rol=ROLE_ADMIN)
        except Rol.DoesNotExist:
            raise CommandError(
                f'No existe el rol {ROLE_ADMIN}. Ejecuta primero: '
                'python manage.py create_initial_data'
            )

        correo = (options.get('username') or self._preguntar('Correo')).lower()
        if '@' not in correo:
            raise CommandError(f'"{correo}" no parece un correo valido.')

        if Usuario.objects.filter(correo=correo).exists():
            raise CommandError(f'Ya existe un usuario con el correo {correo}.')

        curp = self._preguntar('CURP (17 o 18 caracteres)').upper()
        if not CURP_PATTERN.match(curp):
            raise CommandError('La CURP solo admite letras y digitos, de 17 o 18 caracteres.')
        if Usuario.objects.filter(curp=curp).exists():
            raise CommandError('Ya existe un usuario con esa CURP.')

        contrasena = self._preguntar('Contrasena', oculto=True)
        if len(contrasena) < 8:
            raise CommandError('La contrasena debe tener al menos 8 caracteres.')
        if contrasena != self._preguntar('Repite la contrasena', oculto=True):
            raise CommandError('Las contrasenas no coinciden.')

        usuario = UserService.crear_usuario({
            'nombre': self._preguntar('Nombre'),
            'apellido_paterno': self._preguntar('Apellido paterno'),
            'apellido_materno': self._preguntar('Apellido materno', default='-'),
            'correo': correo,
            'contrasena': contrasena,
            'curp': curp,
            'rol': rol_admin,
            'institucion': Institucion.objects.first(),
            'activo': True,
        })

        self.stdout.write(
            self.style.SUCCESS(f'ADMIN creado: {usuario.id_usuario} ({usuario.correo})')
        )