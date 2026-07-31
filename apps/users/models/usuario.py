from django.db import models
from .rol import Rol
from .institucion import Institucion
from django.utils import timezone
from django.contrib.auth.hashers import check_password


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    curp = models.CharField(max_length=18, unique=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    numero_empleado = models.CharField(max_length=20, blank=True, null=True)
    antiguedad = models.CharField(max_length=50, blank=True, null=True)
    nivel_escolar = models.CharField(max_length=100, blank=True, null=True)
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT
    )

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno or ''}".strip()

    class Meta:
        db_table = 'usuarios'
