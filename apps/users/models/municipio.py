from django.db import models
from .estado import Estado

class Municipio(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    clave_municipio = models.CharField(max_length=10)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name="municipios")

    def __str__(self):
        return self.nombre