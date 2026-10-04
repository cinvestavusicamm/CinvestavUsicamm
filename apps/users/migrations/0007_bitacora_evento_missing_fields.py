from django.db import migrations, models


class Migration(migrations.Migration):
    """Alinea bitacora_eventos con el modelo BitacoraEvento.

    Sin esto la bitacora no escribe nada: _registrar_bitacora envuelve la llamada
    en except Exception y solo deja un warning, asi que el fallo pasaba
    inadvertido. Con estos cambios el rastro de auditoria vuelve a funcionar.

    La migracion 0003 creo la tabla con una forma distinta a la del modelo:

    - faltaban las columnas ip_direccion y detalles
    - la PK se llamaba `id` en vez de `id_evento`
    - tipo_evento era varchar(100) en vez de varchar(50)

    La PK se corrige con RenameField, no con la combinacion RemoveField +
    AddField que sugiere el autodetector: esa habria tirado la columna y
    perdido todas las filas.
    """

    dependencies = [
        ("users", "0006_create_proceso_aprobacion_table"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bitacoraevento",
            old_name="id",
            new_name="id_evento",
        ),
        migrations.AlterField(
            model_name="bitacoraevento",
            name="tipo_evento",
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name="bitacoraevento",
            name="ip_direccion",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="bitacoraevento",
            name="detalles",
            field=models.JSONField(blank=True, null=True),
        ),
    ]