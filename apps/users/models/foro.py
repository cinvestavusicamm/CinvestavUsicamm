from django.db import models
from .curso import Curso

class Foro(models.Model):
    id_foro = models.AutoField(primary_key=True)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="foros"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'foros'

    def __str__(self):
        return self.titulo
    
