from django.db import models
from .municipio import Municipio

class CP(models.Model):
    codigo = models.CharField(max_length=10)
    zona = models.CharField(max_length=50)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name="cps")

    def __str__(self):
        return self.codigo