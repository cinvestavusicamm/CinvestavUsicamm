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
            "model": "llama3:8b",
            "prompt": pregunta,
            "options": {
                "temperature": 0.7,
                "num_predict": 256,   
                "num_ctx": 2048     
            }
        }


        r = requests.post(FASTAPI_URL, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()

        respuesta = None

        if 'response' in data:
            respuesta = data['response']

        elif 'results' in data and len(data['results']) > 0:
            respuesta = data['results'][0].get('completion', '')

        elif 'choices' in data and len(data['choices']) > 0:
            respuesta = data['choices'][0].get('text', '')

        if not respuesta:
            respuesta = "El agente no devolvió ninguna respuesta"

        return JsonResponse({'answer': respuesta})

    except requests.exceptions.Timeout:
        return JsonResponse({'answer': 'El agente tardó demasiado en responder'}, status=504)
    except requests.exceptions.ConnectionError:
        return JsonResponse({'answer': 'No se pudo conectar con el agente'}, status=503)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al llamar a FastAPI: {e}")
        return JsonResponse({'answer': 'Error en la comunicación con el agente'}, status=500)
    except Exception as e:
        logger.exception(f"Error inesperado en agente_ajax: {e}")
        return JsonResponse({'answer': 'Ocurrió un error inesperado'})
