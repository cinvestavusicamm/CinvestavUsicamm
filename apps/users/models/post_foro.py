from django.db import models
from .foro import Foro
from .usuario import Usuario

class PostForo(models.Model):
    id_post = models.AutoField(primary_key=True)
    foro = models.ForeignKey(
        Foro,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="posts_foro"
    )
    titulo = models.CharField(max_length=200, blank=True, null=True)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    comentarios_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'posts_foro'

    def __str__(self):
        return f"Post en {self.foro.titulo}"
