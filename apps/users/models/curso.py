from django.db import models
from .usuario import Usuario
from .institucion import Institucion

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)  # nombre → titulo
    descripcion = models.TextField(blank=True, null=True)
    
    docente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cursos_impartidos",
        db_column='id_creador'  
    )
    estado = models.CharField(max_length=50, blank=True, null=True, default='Borrador')
    generado_con_ia = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'cursos'
        managed = False 

    def __str__(self):
        return self.titulo