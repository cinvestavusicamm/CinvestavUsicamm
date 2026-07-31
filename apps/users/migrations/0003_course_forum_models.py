# Generated migration for course and forum models

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_additional_models"),
    ]

    operations = [
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id_curso', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('estado', models.CharField(blank=True, default='Borrador', max_length=50, null=True)),
                ('generado_con_ia', models.BooleanField(default=False)),
                ('version', models.IntegerField(default=1)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_aprobacion', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contenido_json', models.JSONField(blank=True, default=dict, null=True)),
                ('docente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cursos_impartidos',
                    to='users.usuario'
                )),
            ],
            options={
                'db_table': 'cursos',
            },
        ),
        migrations.CreateModel(
            name='Foro',
            fields=[
                ('id_foro', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
                ('curso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='foros',
                    to='users.curso'
                )),
            ],
            options={
                'db_table': 'foros',
            },
        ),
        migrations.CreateModel(
            name='PostForo',
            fields=[
                ('id_post', models.AutoField(primary_key=True, serialize=False)),
                ('contenido', models.TextField()),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
                ('foro', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='posts',
                    to='users.foro'
                )),
                ('autor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='posts_foro',
                    to='users.usuario'
                )),
            ],
            options={
                'db_table': 'posts_foro',
            },
        ),
        migrations.CreateModel(
            name='ProcesoAprobacionCursos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(max_length=50)),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True)),
                ('fecha_revision', models.DateTimeField(blank=True, null=True)),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('curso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='procesos_aprobacion',
                    to='users.curso'
                )),
                ('evaluador', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cursos_evaluados',
                    to='users.usuario'
                )),
            ],
            options={
                'db_table': 'procesos_aprobacion_cursos',
            },
        ),
        migrations.CreateModel(
            name='RetroalimentacionIaCurso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('comentario', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('curso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='retroalimentaciones',
                    to='users.curso'
                )),
            ],
            options={
                'db_table': 'retroalimentaciones_ia_cursos',
            },
        ),
        migrations.CreateModel(
            name='BitacoraEvento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_evento', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('fecha_evento', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bitacora_eventos',
                    to='users.usuario'
                )),
            ],
            options={
                'db_table': 'bitacora_eventos',
            },
        ),
    ]