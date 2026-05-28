from django.db import models

class RetroalimentacionIaCurso(models.Model):
    # Django crea un ID autoincremental por defecto como PK, 
    # pero aquí lo definimos explícitamente para que coincida con tu esquema.
    id_retroalimentacion = models.AutoField(primary_key=True)
    
    # Llave Foránea: Asumiendo que tienes un modelo llamado 'Curso'
   # id_curso = models.ForeignKey(
        #'Curso', 
    #    on_delete=models.CASCADE, 
     #   db_column='id_curso'
    #)
    
    sugerencias = models.TextField()
    confianza_pbt = models.DecimalField(max_digits=5, decimal_places=2)
    version = models.IntegerField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'retroalimentacion_ia_curso'
        verbose_name = 'Retroalimentación IA Curso'