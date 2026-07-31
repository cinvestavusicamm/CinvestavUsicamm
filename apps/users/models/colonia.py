from django.db import models
from .cp import CP

class Colonia(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    cp = models.ForeignKey(CP, on_delete=models.CASCADE, related_name="colonias")

    def __str__(self):
        return self.nombre