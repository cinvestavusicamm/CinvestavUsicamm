from django.db import models
from .usuario import Usuario
from .estado import Estado

class ProcesoEscalafon(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="procesos")
    folio = models.CharField(max_length=50)
    tipo_proceso = models.CharField(max_length=50)
    ciclo_escolar = models.CharField(max_length=20)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    funcion = models.CharField(max_length=100)
    tipo_sostenimiento = models.CharField(max_length=50)
    tipo_valoracion = models.TextField()
    datos_multifactores = models.JSONField()
    estatus = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.folio