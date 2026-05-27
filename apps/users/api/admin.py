"""
API endpoints administrativos
"""
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from apps.users.config.constants import ROLE_ADMIN
from apps.users.services.permisos import requiere_rol


def _tipo_columna(descripcion_columna):
    """Obtiene el tipo de columna de la descripción"""
    try:
        return connection.introspection.get_field_type(
            descripcion_columna.type_code,
            descripcion_columna,
        )
    except Exception:
        return str(descripcion_columna.type_code)


def _restricciones_por_columna(restricciones):
    """Procesa restricciones por columna"""
    columnas = {}

    for nombre_restriccion, restriccion in restricciones.items():
        for columna in restriccion.get("columns", []):
            datos_columna = columnas.setdefault(
                columna,
                {
                    "primary_key": False,
                    "unique": False,
                    "foreign_keys": [],
                    "indexes": [],
                },
            )

            if restriccion.get("primary_key"):
                datos_columna["primary_key"] = True

            if restriccion.get("unique"):
                datos_columna["unique"] = True

            if restriccion.get("foreign_key"):
                tabla, columna_referenciada = restriccion["foreign_key"]
                datos_columna["foreign_keys"].append(
                    {
                        "constraint": nombre_restriccion,
                        "table": tabla,
                        "column": columna_referenciada,
                    }
                )

            if restriccion.get("index"):
                datos_columna["indexes"].append(nombre_restriccion)

    return columnas


def _contar_filas(cursor, tabla):
    """Cuenta filas de una tabla"""
    nombre_tabla = connection.ops.quote_name(tabla)
    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
    return cursor.fetchone()[0]


def _obtener_tablas_bd():
    """Obtiene todas las tablas de la base de datos"""
    tablas = []

    with connection.cursor() as cursor:
        tablas_bd = connection.introspection.get_table_list(cursor)

        for tabla_info in sorted(tablas_bd, key=lambda tabla: tabla.name):
            restricciones = connection.introspection.get_constraints(
                cursor,
                tabla_info.name,
            )
            restricciones_columnas = _restricciones_por_columna(restricciones)
            columnas = []

            for columna in connection.introspection.get_table_description(
                cursor,
                tabla_info.name,
            ):
                datos_restricciones = restricciones_columnas.get(
                    columna.name,
                    {
                        "primary_key": False,
                        "unique": False,
                        "foreign_keys": [],
                        "indexes": [],
                    },
                )

                columnas.append(
                    {
                        "name": columna.name,
                        "type": _tipo_columna(columna),
                        "database_type": str(columna.type_code),
                        "nullable": columna.null_ok,
                        "default": getattr(columna, "default", None),
                        "primary_key": datos_restricciones["primary_key"],
                        "unique": datos_restricciones["unique"],
                        "foreign_keys": datos_restricciones["foreign_keys"],
                        "indexes": datos_restricciones["indexes"],
                    }
                )

            tablas.append(
                {
                    "name": tabla_info.name,
                    "type": tabla_info.type,
                    "row_count": _contar_filas(cursor, tabla_info.name),
                    "columns": columnas,
                }
            )

    return tablas


@require_GET
@requiere_rol(ROLE_ADMIN)
def listar_tablas_bd(request):
    """API endpoint para listar tablas de la base de datos (solo admin)"""
    tablas = _obtener_tablas_bd()
    total_columnas = sum(len(tabla["columns"]) for tabla in tablas)
    total_filas = sum(tabla["row_count"] for tabla in tablas)

    if (
        request.GET.get("format") == "json"
        or "application/json" in request.headers.get("Accept", "")
    ):
        return JsonResponse(
            {
                "estado": "ok",
                "mensaje": "Tablas de la base de datos obtenidas correctamente",
                "datos": {
                    "total_tablas": len(tablas),
                    "total_columnas": total_columnas,
                    "total_filas": total_filas,
                    "tablas": tablas,
                },
            },
            json_dumps_params={"ensure_ascii": False},
        )

    return render(
        request,
        "admin/bd_tablas.html",
        {
            "tablas": tablas,
            "total_tablas": len(tablas),
            "total_columnas": total_columnas,
            "total_filas": total_filas,
            "usuario_nombre": request.session.get("usuario_nombre"),
            "usuario_rol": request.session.get("usuario_rol"),
        },
    )
