# Generated migration to add missing fields identified from templates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_course_forum_models"),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='numero_empleado',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='antiguedad',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='nivel_escolar',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='postforo',
            name='titulo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='postforo',
            name='fecha_edicion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='postforo',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postforo',
            name='comentarios_count',
            field=models.IntegerField(default=0),
        ),
        # BitacoraEvento fields already added manually to database
        migrations.RunSQL(
            sql="SELECT 1",  # No-op, fields already exist
            reverse_sql="SELECT 1"
        ),
    ]