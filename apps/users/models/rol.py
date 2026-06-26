from django.db import models


class Rol(models.Model):
    id_rol      = models.AutoField(primary_key=True)
    nombre_rol  = models.CharField(max_length=50, unique=True)
    #descripcion = models.TextField(blank=True, null=True)
    #activo      = models.BooleanField(default=True)
    #created_at  = models.DateTimeField(auto_now_add=True)
    #updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_rol

    class Meta:
        db_table  = 'roles'
        managed   = False
        ordering  = ['nombre_rol']
