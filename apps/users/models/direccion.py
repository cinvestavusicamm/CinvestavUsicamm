from django.db import models
from .colonia import Colonia
from .tipo_hogar import TipoHogar

class Direccion(models.Model):
    calle = models.CharField(max_length=150)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, null=True, blank=True)

    colonia = models.ForeignKey(Colonia, on_delete=models.CASCADE, related_name="direcciones")
    tipo_hogar = models.ForeignKey(TipoHogar, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.calle} #{self.numero_exterior}"