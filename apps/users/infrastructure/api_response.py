from django.http import JsonResponse


def respuesta_ok(request, mensaje="Operacion exitosa", datos=None, status=200):
    payload = {
        "estado": "ok",
        "mensaje": mensaje,
        "datos": datos,
        "errores": None,
    }
    return JsonResponse(payload, status=status)


def respuesta_error(request, mensaje="Ocurrio un error", errores=None, status=400):
    resolved_message = mensaje
    resolved_errors = errores

    if errores is None and not isinstance(mensaje, str):
        resolved_message = "Solicitud invalida"
        resolved_errors = mensaje
    elif errores is None:
        resolved_errors = {"detalle": [mensaje]}

    payload = {
        "estado": "error",
        "mensaje": resolved_message,
        "datos": None,
        "errores": resolved_errors,
    }
    return JsonResponse(payload, status=status)
