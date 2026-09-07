from django.db import models

class Estado(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    clave_estado = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre