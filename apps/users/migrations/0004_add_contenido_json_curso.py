from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_retroalimentacioniacurso_bitacoraevento_curso_foro_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='curso',
            name='contenido_json',
            field=models.JSONField(null=True, blank=True, default=dict),
        ),
    ]
