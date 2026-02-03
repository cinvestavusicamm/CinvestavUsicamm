import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://ia_service_core:8003/api/ask"

@csrf_exempt
def agente_ajax(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'answer': 'No autorizado'}, status=401)

    if request.method != "POST":
        return JsonResponse({'answer': 'Método no permitido'}, status=405)

    pregunta = request.POST.get('pregunta', '').strip()
    if not pregunta:
        return JsonResponse({'answer': 'No se recibió pregunta'}, status=400)

    try:
        payload = {
            "prompt": pregunta
        }


        r = requests.post(
            FASTAPI_URL,
            json=payload,
            timeout=180
        )
        r.raise_for_status()
        data = r.json()

        respuesta = data.get("response")

        if not respuesta:
            respuesta = "No se pudo generar una respuesta"


        if not respuesta:
            respuesta = "No se pudo generar una respuesta"

        return JsonResponse({"answer": respuesta})

    except Exception as e:
        logger.exception(f"Error inesperado en agente_ajax: {e}")
        return JsonResponse({'answer': 'Ocurrió un error inesperado'})
