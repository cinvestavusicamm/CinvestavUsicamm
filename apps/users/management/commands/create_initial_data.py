from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.users.models import Rol, Institucion, Usuario, Curso
from django.utils import timezone


class Command(BaseCommand):
    help = 'Crea datos iniciales para pruebas'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales...')

        # Crear roles
        for nombre_rol in ('ADMIN', 'DOCENTE', 'EVALUADOR', 'GENERADOR'):
            rol, created = Rol.objects.get_or_create(nombre_rol=nombre_rol)
            if created:
                self.stdout.write(f'Rol creado: {rol.nombre_rol}')
            else:
                self.stdout.write(f'Rol ya existe: {rol.nombre_rol}')

        # Crear institución
        institucion = Institucion.objects.filter(nombre='Institución de Prueba').first()
        if institucion is None:
            institucion = Institucion.objects.create(
                nombre='Institución de Prueba',
                tipo='Educación Básica',
                activo=True,
            )
            self.stdout.write(f'Institución creada: {institucion.nombre}')
        else:
            self.stdout.write(f'Institución ya existe: {institucion.nombre}')

        # Crear usuario administrador
        rol_admin = Rol.objects.get(nombre_rol='ADMIN')
        admin_password = 'Admin123!'  # Contraseña que cumple con requisitos
        
        admin, created = Usuario.objects.get_or_create(
            curp='ADMI900101HDFRRN01',
            defaults={
                'nombre': 'Administrador',
                'apellido_paterno': 'Sistema',
                'apellido_materno': 'Prueba',
                'correo': 'admin@prueba.com',
                'contrasena': make_password(admin_password),
                'fecha_registro': timezone.now(),
                'ultimo_acceso': timezone.now(),
                'activo': True,
                'rol': rol_admin,
                'institucion': institucion
            }
        )
        if created:
            self.stdout.write(f'Usuario administrador creado: {admin.correo}')
            self.stdout.write(f'Contraseña: {admin_password}')
        else:
            self.stdout.write(f'Usuario administrador ya existe: {admin.correo}')

        # Crear curso de prueba
        curso = Curso.objects.filter(titulo='Curso de Prueba').first()
        if curso is None:
            curso = Curso.objects.create(
                titulo='Curso de Prueba',
                descripcion='Este es un curso de prueba para el sistema',
                estado='Borrador',
                generado_con_ia=False,
                version=1,
                contenido_json={'modulos': []},
                docente=admin,
            )
            self.stdout.write(f'Curso creado: {curso.titulo}')
        else:
            self.stdout.write(f'Curso ya existe: {curso.titulo}')

        self.stdout.write(self.style.SUCCESS('Datos iniciales creados exitosamente!'))