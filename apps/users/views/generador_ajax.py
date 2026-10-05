import requests
from django.conf import settings
from django.http import StreamingHttpResponse
import logging
import json
from apps.users.utils.api_response import respuesta_ok, respuesta_error
from apps.users.services.router_service import RouterService
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.permisos import requiere_rol

logger = logging.getLogger(__name__)

AI_AGENT_SERVICE_URL = getattr(settings, 'AI_AGENT_SERVICE_URL', 'http://ms_ai_agent_service:8107').rstrip('/')
IA_AGENT_CHAT_URL = getattr(settings, 'IA_AGENT_CHAT_URL', f'{AI_AGENT_SERVICE_URL}/api/v1/ai/chat').rstrip('/')
IA_AGENT_STREAM_URL = getattr(settings, 'IA_AGENT_STREAM_URL', f'{AI_AGENT_SERVICE_URL}/api/v1/ai/chat/stream').rstrip('/')

FASTAPI_URL = IA_AGENT_CHAT_URL
FASTAPI_STREAM_URL = IA_AGENT_STREAM_URL


# Sin consumidor conocido: ningun JS ni template hace POST a esta ruta
# exacta. Queda protegida por rol para que, si alguien la llama, sea solo
# un GENERADOR. Candidata a retirada, pendiente de revisar el flujo de
# cursos con IA (ver PLAN.md).
# Sin @csrf_exempt: sin consumidor al que avisar del fallo. Si aparece
# uno, necesita la cookie csrftoken y un {% csrf_token %} en su pagina.
@requiere_rol(ROLE_GENERADOR)
def generador_ajax(request):
    if request.method != "POST":
        return respuesta_error(
            mensaje="Método no permitido",
            status=405
        )

    pregunta = request.POST.get('pregunta', '').strip()

    if not pregunta:
        return respuesta_error(
            mensaje="La pregunta no puede estar vacía",
            status=400
        )

    # 🔥 DECISIÓN DEL ROUTER (PRIMERO)
    tipo = RouterService.decidir(pregunta)

    # 👉 SI ES BD, NO VA A IA
    if tipo == "bd":
        return respuesta_ok(
            mensaje="Consulta resuelta desde base de datos",
            data={"answer": "Consulta detectada como BD"}
        )

    # 👇 SOLO SI ES AGENTE
    usar_stream = request.POST.get('stream') == 'true'

    if usar_stream:
        return generador_streaming(pregunta)

    try:
        payload = {"prompt": pregunta}

        r = requests.post(
            FASTAPI_URL,
            json=payload,
            timeout=180
        )
        r.raise_for_status()
        data = r.json()

        respuesta = data.get("response") or data.get("reply") or data.get("answer") or "No se pudo generar una respuesta"
        return respuesta_ok(
            mensaje="Respuesta generada correctamente",
            data={"answer": respuesta}
        )

    except Exception as e:
        logger.exception(f"Error inesperado en generador_ajax: {e}")
        return respuesta_error(
            mensaje="Ocurrió un error inesperado",
            errors=str(e),
            status=500
        )


def generador_streaming(pregunta):

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