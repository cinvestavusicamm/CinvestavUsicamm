from django.db import models
from .usuario import Usuario

class BitacoraEvento(models.Model):
    id_evento = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    tipo_evento = models.CharField(max_length=50)
    descripcion = models.TextField()
    fecha_evento = models.DateTimeField(auto_now_add=True)
    ip_direccion = models.CharField(max_length=50, blank=True, null=True)
    detalles = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'bitacora_eventos'

    def __str__(self):
        return f"{self.usuario} - {self.tipo_evento} - {self.fecha_evento}"
        
