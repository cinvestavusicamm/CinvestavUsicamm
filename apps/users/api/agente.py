"""
API endpoints para el agente de IA
"""
import requests
import json
import logging
from django.http import StreamingHttpResponse
from apps.users.config.constants import ROLE_ADMIN, ROLE_EVALUADOR
from apps.users.infrastructure.api_response import respuesta_ok, respuesta_error
from apps.users.services.permisos import requiere_rol
from apps.users.services.router_service import RouterService

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://ia_service_core:8003/api/ask"
FASTAPI_STREAM_URL = "http://ia_service_core:8003/api/ask/stream"


# El rol se comprueba contra la base, no contra la cookie. ADMIN porque es
# el unico consumidor hoy (chatbot-admin.js, que carga paneladm.html);
# EVALUADOR porque las ocho plantillas de templates/Evaluador/ ya preparan
# esta URL para un chat que todavia no existe (DEUDA-5). Si ese chat se
# rehabilita, el consumidor aparece y este rol queda justo; si se decide
# que no, se quita EVALUADOR de la lista.
#
# Sin @csrf_exempt a proposito: el token llega de la cookie csrftoken, que
# paneladm.html emite con sus dos {% csrf_token %}. Con csrf_exempt el
# token se enviaba pero no se validaba, y eso dejaba el endpoint abierto a
# CSRF para cualquier pagina externa con la sesion de la victima.
@requiere_rol(ROLE_ADMIN, ROLE_EVALUADOR)
def agente_ajax(request):
    """API endpoint para interactuar con el agente de IA"""
    if request.method != "POST":
        return respuesta_error(
            request,
            mensaje="Método no permitido",
            status=405
        )

    pregunta = request.POST.get('pregunta', '').strip()
    usar_stream = request.POST.get('stream') == 'true'

    if not pregunta:
        return respuesta_error(
            request,
            mensaje="La pregunta no puede estar vacía",
            status=400
        )

    destino = RouterService.decidir(pregunta)
    if destino == "bd":
        try:
            respuesta = RouterService.responder_desde_bd(
                pregunta,
                usuario_id=request.session.get("usuario_id"),
            )
            return respuesta_ok(
                request,
                mensaje="Respuesta obtenida desde la base de datos",
                datos={"answer": respuesta, "source": "bd"},
            )
        except Exception as e:
            logger.exception(f"Error consultando la base de datos desde agente_ajax: {e}")
            return respuesta_error(
                request,
                mensaje="No se pudo consultar la base de datos",
                errores=str(e),
                status=500,
            )

    if usar_stream:
        return agente_streaming(pregunta)

    try:
        payload = {
            "prompt": pregunta,
            "role": "teacher",
            "user_id": str(request.session.get("usuario_id", "anon"))
        }

        headers = {
            "Content-Type": "application/json",
            "X-Internal-Service-Key": "clave_estricta_por_defecto_cambiar_en_prod"
        }

        r = requests.post(
            FASTAPI_URL,
            json=payload,
            headers=headers,
            timeout=180
        )
        r.raise_for_status()
        data = r.json()

        respuesta = data.get("response", "No se pudo generar una respuesta")
        return respuesta_ok(
            request,
            mensaje="Respuesta generada correctamente",
            datos={"answer": respuesta, "source": "agente"}
        )

    except Exception as e:
        logger.exception(f"Error inesperado en agente_ajax: {e}")
        return respuesta_error(
            request,
            mensaje="Ocurrió un error inesperado",
            errores=str(e),
            status=500
        )


def agente_streaming(pregunta):
    """Genera respuesta streaming del agente"""
    logger.info(f"Iniciando streaming para pregunta: {pregunta[:50]}...")

    def generar_stream():
        try:
            logger.info(f"Conectando a FASTAPI_STREAM_URL: {FASTAPI_STREAM_URL}")
            
            with requests.post(
                FASTAPI_STREAM_URL,
                json={"prompt": pregunta},
                stream=True,
                timeout=(30, None)
            ) as r:
                logger.info(f"Respuesta del servicio: status={r.status_code}")
                
                if r.status_code != 200:
                    yield f"data: {json.dumps({'error': f'Error del servicio: {r.status_code}'})}\n\n"
                    return
                
                line_count = 0
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    
                    line_count += 1
                    logger.debug(f"Línea recibida {line_count}: {line[:100]}")

                    if line.startswith("data:"):
                        line = line[len("data:"):].strip()

                    try:
                        data = json.loads(line)
                        logger.debug(f"Datos parseados: {data}")

                        if data.get("type") == "content":
                            token = data.get("token", "")
                            logger.debug(f"Enviando token: {token}")
                            yield f"data: {json.dumps({'token': token})}\n\n"

                        elif data.get("type") == "done":
                            logger.info("Stream completado")
                            yield f"data: {json.dumps({'done': True})}\n\n"

                    except json.JSONDecodeError as e:
                        logger.error(f"Error parseando JSON: {e}, línea: {line}")
                        continue

                if line_count == 0:
                    logger.warning("No se recibieron líneas del servicio")
                    yield f"data: {json.dumps({'error': 'No se recibió respuesta del asistente'})}\n\n"

        except requests.exceptions.Timeout:
            logger.error("Timeout conectando al servicio")
            yield f"data: {json.dumps({'error': 'Tiempo de espera agotado'})}\n\n"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión: {e}")
            yield f"data: {json.dumps({'error': 'No se pudo conectar con el asistente'})}\n\n"
        except Exception as e:
            logger.exception(f"Error inesperado en streaming: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    response = StreamingHttpResponse(
        generar_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Connection'] = 'keep-alive'

    return response
