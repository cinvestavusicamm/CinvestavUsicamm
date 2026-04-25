from django.db import models
from .usuario import Usuario
#from .curso import Curso


class ProcesoAprobacionCursos(models.Model):
    id_proceso = models.AutoField(
        primary_key=True,
        db_column='id_proceso'
    )

    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        db_column='id_curso',
        related_name='aprobaciones'
    )

    evaluador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_evaluador',
        related_name='evaluaciones_realizadas'
    )

    iteracion = models.CharField(max_length=50)

    decision = models.CharField(max_length=50)

    comentarios = models.TextField()

    fecha_revision = models.DateTimeField()

    class Meta:
        db_table = 'proceso_aprobacion_cursos'

    def __str__(self):
        return f"{self.curso} - {self.decision}"