from django.http import JsonResponse


def respuesta_ok(data=None, mensaje="Operación exitosa", status=200):
    """
    Retorna una respuesta JSON exitosa
    """
    response_data = {
        "success": True,
        "mensaje": mensaje,
        "data": data
    }
    return JsonResponse(response_data, status=status)


def respuesta_error(mensaje="Error en la operación", errors=None, status=400):
    """
    Retorna una respuesta JSON de error
    """
    response_data = {
        "success": False,
        "mensaje": mensaje,
        "errors": errors
    }
    return JsonResponse(response_data, status=status)
