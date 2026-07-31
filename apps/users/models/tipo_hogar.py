from django.db import models

class TipoHogar(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre