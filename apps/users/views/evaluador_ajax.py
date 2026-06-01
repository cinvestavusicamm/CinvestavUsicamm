import requests
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from apps.users.utils.api_response import respuesta_ok, respuesta_error
from apps.users.services.router_service import RouterService

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://ia_service_core:8003/api/ask"
FASTAPI_STREAM_URL = "http://ia_service_core:8003/api/ask/stream"


@csrf_exempt
def evaluador_ajax(request):
    if not request.session.get('usuario_id'):
        return respuesta_error(
            request,
            mensaje="No autorizado",
            status=401
        )

    if request.method != "POST":
        return respuesta_error(
            request,
            mensaje="Método no permitido",
            status=405
        )

    pregunta = request.POST.get('pregunta', '').strip()

    if not pregunta:
        return respuesta_error(
            request,
            mensaje="La pregunta no puede estar vacía",
            status=400
        )

    # 🔥 DECISIÓN DEL ROUTER (PRIMERO)
    tipo = RouterService.decidir(pregunta)

    # 👉 SI ES BD, NO VA A IA
    if tipo == "bd":
        return respuesta_ok(
            request,
            mensaje="Consulta resuelta desde base de datos",
            datos={"answer": "Consulta detectada como BD"}
        )

    # 👇 SOLO SI ES AGENTE
    usar_stream = request.POST.get('stream') == 'true'

    if usar_stream:
        return evaluador_streaming(pregunta)

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
        return respuesta_ok(
            request,
            mensaje="Respuesta generada correctamente",
            datos={"answer": respuesta}
        )

    except Exception as e:
        logger.exception(f"Error inesperado en evaluador_ajax: {e}")
        return respuesta_error(
            request,
            mensaje="Ocurrió un error inesperado",
            errores=str(e),
            status=500
        )


def evaluador_streaming(pregunta):

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
                            yield f"data: {json.dumps({'estado': 'ok', 'token': token})}\n\n"

                        elif data.get("type") == "done":
                            yield f"data: {json.dumps({'estado': 'ok', 'done': True})}\n\n"

                    except:
                        continue

        except Exception as e:
            logger.exception(f"Error en streaming: {e}")
            yield f"data: {json.dumps({'estado': 'error', 'error': str(e)})}\n\n"

    response = StreamingHttpResponse(
        generar_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Connection'] = 'keep-alive'

    return response