from django.contrib import admin
from . import (
    Usuario, Rol, Institucion,
    Direccion, Estado, Municipio,
    CP, Colonia, TipoHogar,
    ProcesoEscalafon, Document, Prom
)
admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Institucion)
admin.site.register(Direccion)
admin.site.register(Estado)
admin.site.register(Municipio)
admin.site.register(CP)
admin.site.register(Colonia)
admin.site.register(TipoHogar)
admin.site.register(ProcesoEscalafon)
admin.site.register(Document)
admin.site.register(Prom)