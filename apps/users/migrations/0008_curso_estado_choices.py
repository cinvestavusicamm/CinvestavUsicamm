from django.db import migrations, models


class Migration(migrations.Migration):
    """Anota las choices del estado de curso.

    Escrita a mano y no con makemigrations porque el autodetector se detiene a
    preguntar por una deriva que no es de este cambio
    (`retroalimentacioniacurso.fecha` frente a `retroalimentacioniacurso.
    fecha_generacion`, ambos auto_now_add y sin relacion entre si). Contestar
    ahi mezclaba en esta migracion un RenameField de otro modelo.

    Que sea solo un AlterField sin tocar la columna es lo importante: `choices`
    no se aplica en la base, asi que las filas que ya tengan un estado fuera de
    la lista -- y hay, porque hasta ahora el campo no tenia ninguna -- siguen
    intactas. El orden de este commit lo deja demostrado en el propio fichero
    de tests.
    """

    dependencies = [
        ('users', '0007_bitacora_evento_missing_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curso',
            name='estado',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Borrador', 'Borrador'),
                    ('En_Revisión', 'En_Revisión'),
                    ('Aprobado', 'Aprobado'),
                    ('Rechazado', 'Rechazado'),
                    ('Inactivo', 'Inactivo'),
                ],
                default='Borrador',
                max_length=50,
                null=True,
            ),
        ),
    ]