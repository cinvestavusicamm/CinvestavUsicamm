from django.db import models
from .usuario import Usuario
from .institucion import Institucion

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    docente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cursos_impartidos",
        db_column='docente_id'
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.CASCADE,
        db_column='institucion_id'
    )
    ciclo_escolar = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'cursos'

    def __str__(self):
        return self.nombre
