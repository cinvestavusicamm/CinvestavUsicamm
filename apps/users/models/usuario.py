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

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column='rol_id'
    )

    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        db_column='institucion_id'
    )

    class Meta:
        db_table = 'usuarios'
        managed = False
