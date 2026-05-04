from django.db import models
from .foro import Foro
from .usuario import Usuario

class PostForo(models.Model):
    id_post = models.AutoField(primary_key=True)
    foro = models.ForeignKey(
        Foro,
        on_delete=models.CASCADE,
        related_name="posts",
        db_column='foro_id'
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='autor_id'
    )
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts_foro'

    def __str__(self):
        return f"Post en {self.foro.titulo}"
