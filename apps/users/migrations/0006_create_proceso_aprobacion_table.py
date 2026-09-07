# Generated migration to create proceso_aprobacion_cursos table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_add_missing_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcesoAprobacionCursos',
            fields=[
                ('id_proceso', models.AutoField(db_column='id_proceso', primary_key=True, serialize=False)),
                ('curso', models.ForeignKey(blank=True, db_column='id_curso', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aprobaciones', to='users.curso')),
                ('evaluador', models.ForeignKey(db_column='id_evaluador', on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones_realizadas', to='users.usuario')),
                ('iteracion', models.CharField(max_length=50)),
                ('decision', models.CharField(max_length=50)),
                ('comentarios', models.TextField()),
                ('fecha_revision', models.DateTimeField()),
            ],
            options={
                'db_table': 'proceso_aprobacion_cursos',
            },
        ),
    ]
