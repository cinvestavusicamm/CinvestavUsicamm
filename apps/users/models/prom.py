from django.db import models

class Prom(models.Model):
    id = models.BigAutoField(primary_key=True)
    folio = models.CharField(max_length=50)
    curp = models.CharField(max_length=18)
    nombre = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50)
    correo1 = models.EmailField()
    correo2 = models.EmailField(null=True, blank=True)
    telefono1 = models.CharField(max_length=15)
    telefono2 = models.CharField(max_length=15, null=True, blank=True)
    entidad = models.CharField(max_length=50)
    cct = models.CharField(max_length=50)
    subsistema = models.CharField(max_length=120)
    sistema = models.CharField(max_length=50)
    cargo = models.CharField(max_length=50)
    funcion = models.CharField(max_length=50)
    cargo_val = models.CharField(max_length=50)
    tipo_val = models.CharField(max_length=120)
    estudios_posgrado = models.CharField(max_length=50)
    exp_fds = models.CharField(max_length=50)

    def __str__(self):
        return self.folio