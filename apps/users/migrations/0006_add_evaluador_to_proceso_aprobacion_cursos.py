# Generated migration to add missing evaluador field

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_curso_options_alter_rol_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='procesoaprobacioncursos',
            name='evaluador',
            field=models.ForeignKey(
                db_column='id_evaluador',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='evaluaciones_realizadas',
                to='users.usuario'
            ),
        ),
    ]
