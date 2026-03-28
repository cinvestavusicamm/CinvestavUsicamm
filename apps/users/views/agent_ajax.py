import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://ia_service_core:8003/api/ask"
FASTAPI_STREAM_URL = "http://ia_service_core:8003/api/ask/stream"


@csrf_exempt
def agente_ajax(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'answer': 'No autorizado'}, status=401)

    if request.method != "POST":
        return JsonResponse({'answer': 'Método no permitido'}, status=405)

    pregunta = request.POST.get('pregunta', '').strip()
    usar_stream = request.POST.get('stream') == 'true'

    if not pregunta:
        return JsonResponse({'answer': 'No se recibió pregunta'}, status=400)

    if usar_stream:
        return agente_streaming(pregunta)

    try:
        payload = {"prompt": pregunta}

        r = requests.post(
            FASTAPI_URL,
            json=payload,
            timeout=180
        )
        r.raise_for_status()
        data = r.json()

        respuesta = data.get("response", "No se pudo generar una respuesta")
        return JsonResponse({"answer": respuesta})

    except Exception as e:
        logger.exception(f"Error inesperado en agente_ajax: {e}")
        return JsonResponse({'answer': 'Ocurrió un error inesperado'})


def agente_streaming(pregunta):
    """Vista para streaming de respuestas tipo SSE"""

    def generar_stream():
        try:
            with requests.post(
                FASTAPI_STREAM_URL,
                json={"prompt": pregunta},
                stream=True,
                timeout=(30, None)
            ) as r:

                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    if line.startswith("data:"):
                        line = line[len("data:"):].strip()

                    try:
                        data = json.loads(line)

                        if data.get("type") == "content":
                            token = data.get("token", "")
                            # Enviar cada token inmediatamente sin esperar espacios
                            yield f"data: {token}\n\n"

                        elif data.get("type") == "done":
                            yield "data: [DONE]\n\n"

                    except:
                        continue

        except Exception as e:
            logger.exception(f"Error en streaming: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    response = StreamingHttpResponse(
        generar_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Connection'] = 'keep-alive'

    return response