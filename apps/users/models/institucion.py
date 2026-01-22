from django.db import models

class Institucion(models.Model):
    id_institucion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    domicilio = models.TextField()
    claves = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'instituciones'
        managed = False
