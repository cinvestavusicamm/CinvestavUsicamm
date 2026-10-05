"""
API endpoints para el agente de IA
"""
import requests
import json
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import StreamingHttpResponse
from apps.users.config.constants import ROLE_ADMIN, ROLE_EVALUADOR
from apps.users.infrastructure.api_response import respuesta_ok, respuesta_error
from apps.users.services.permisos import requiere_rol
from apps.users.services.router_service import RouterService

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://ia_service_core:8003/api/ask"
FASTAPI_STREAM_URL = "http://ia_service_core:8003/api/ask/stream"


def clave_del_servicio():
    """Clave compartida con el microservicio de IA.

    Sale del entorno (INTERNAL_SERVICE_KEY). Antes estaba escrita en este
    archivo, con lo que el repositorio llevaba una credencial de servicio
    versionada y no se podia rotar sin tocar codigo.

    Sin valor por defecto a proposito: si la clave no esta definida, prefiero
    un fallo ruidoso antes que mandar una cadena vacia o un literal de
    repuesto. Una cadena vacia pasaria el chequeo del microservicio solo
    si este tambien aceptase vacio, y un literal de repuesto seria volver
    a la credencial en el codigo. El error se propaga tal cual: es un
    despliegue mal configurado, no un error del usuario que pregunta.
    """
    clave = getattr(settings, 'INTERNAL_SERVICE_KEY', '') or ''
    if not clave.strip():
        raise ImproperlyConfigured(
            'INTERNAL_SERVICE_KEY no esta definida, asi que no se puede '
            'autenticar contra el microservicio de IA (/agente-ajax/). '
            'Definela en el entorno -- en desarrollo, en el .env local; en '
            'produccion, en las variables del despliegue -- con el mismo '
            'valor que lea el microservicio de IA. No hay valor por defecto '
            'a proposito. Ver INTERNAL_SERVICE_KEY en .env.example.'
        )
    return clave


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
        except Exception:
            # La excepcion entera se queda en el log. Antes se devolvia con
            # errores=str(e), que al usuario le llegaba el texto de la libreria
            # de base de datos, con la consulta y a veces la estructura de las
            # tablas.
            logger.exception('No se pudo consultar la base de datos desde agente_ajax')
            return respuesta_error(
                request,
                mensaje="No se pudo consultar la base de datos",
                status=500,
            )

    if usar_stream:
        return agente_streaming(pregunta)

    # Fuera del try de abajo: ese bloque convierte cualquier Exception en un
    # 500 de "ocurrio un error inesperado" con el detalle dentro, y una clave
    # sin configurar no es un fallo del microservicio sino un despliegue roto.
    # Ahi dentro el mensaje claro se perderia.
    clave = clave_del_servicio()

    try:
        payload = {
            "prompt": pregunta,
            "role": "teacher",
            "user_id": str(request.session.get("usuario_id", "anon"))
        }

        headers = {
            "Content-Type": "application/json",
            "X-Internal-Service-Key": clave
        }

        r = requests.post(
            FASTAPI_URL,
            json=payload,
            headers=headers,
            timeout=settings.IA_SERVICE_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        # Antes data.get("response", "no se pudo generar..."): si la clave del JSON
        # estaba mal, el usuario leia un mensaje que parece un fallo del modelo
        # cuando en realidad el servicio contesto otra cosa. Ahora se distingue:
        # si el campo no esta, se dice que la respuesta vino incompleta, que es
        # un fallo del servicio y no del modelo.
        if "response" not in data:
            logger.error(
                'Respuesta sin campo "response" de %s. Claves recibidas: %s',
                FASTAPI_URL, sorted(data) if isinstance(data, dict) else type(data).__name__,
            )
            return respuesta_error(
                request,
                mensaje='El asistente devolvio una respuesta incompleta. Intenta de nuevo.',
                status=502,
            )

        return respuesta_ok(
            request,
            mensaje="Respuesta generada correctamente",
            datos={"answer": data["response"], "source": "agente"}
        )

    except requests.exceptions.Timeout:
        # Distinto del "error inesperado" de abajo porque la accion es otra: no
        # se reintenta igual, la pregunta era larga o el modelo se atasco.
        logger.error('Timeout de %ss hablando con el asistente', settings.IA_SERVICE_TIMEOUT)
        return respuesta_error(
            request,
            mensaje='El asistente esta tardando demasiado. Prueba con una pregunta mas corta.',
            status=504,
        )
    except requests.exceptions.ConnectionError:
        # El servicio no contesto: no arranco, se cayo o no hay red. El log
        # lleva la excepcion entera; al usuario le basta con saber que no esta.
        logger.exception('No se pudo conectar con el microservicio de IA')
        return respuesta_error(
            request,
            mensaje='El asistente no esta disponible. Intenta en unos momentos.',
            status=503,
        )
    except requests.exceptions.HTTPError as e:
        # El microservicio respondio con 4xx/5xx. La causa va al log; el codigo
        # se traduce porque un 401 del microservicio significa clave mal puesta
        # en el despliegue, que el usuario no puede arreglar.
        logger.error('El asistente respondio con error HTTP: %s', e.response.status_code)
        return respuesta_error(
            request,
            mensaje='El asistente no pudo procesar la pregunta. Intenta de nuevo.',
            status=502,
        )
    except ValueError:
        # r.json() sobre un cuerpo que no es JSON. Es una respuesta invalida del
        # servicio, no un problema de la pregunta del usuario.
        logger.exception('El asistente devolvio algo que no es JSON')
        return respuesta_error(
            request,
            mensaje='El asistente devolvio una respuesta que no se pudo leer.',
            status=502,
        )
    except Exception:
        # Se registra entero y no se devuelve str(e): antes el usuario recibia la
        # excepcion de la libreria, con URL interna y a veces la clave.
        logger.exception('Error inesperado en agente_ajax')
        return respuesta_error(
            request,
            mensaje="Ocurrió un error inesperado",
            status=500,
        )


def agente_streaming(pregunta):
    """Genera respuesta streaming del agente"""
    logger.info(f"Iniciando streaming para pregunta: {pregunta[:50]}...")

    def generar_stream():
        try:
            logger.info(f"Conectando a FASTAPI_STREAM_URL: {FASTAPI_STREAM_URL}")
            
            # El None de antes era un timeout de lectura infinito: si el
            # servicio se colgaba sin cerrar la conexion, esta peticion se
            # quedaba ocupando un worker de gunicorn indefinidamente. Con dos
            # valores, uno para conectar y otro para leer, se acaba solo.
            with requests.post(
                FASTAPI_STREAM_URL,
                json={"prompt": pregunta},
                stream=True,
                timeout=(
                    settings.IA_SERVICE_CONNECT_TIMEOUT,
                    settings.IA_SERVICE_READ_TIMEOUT,
                )
            ) as r:
                logger.info(f"Respuesta del servicio: status={r.status_code}")

                if r.status_code != 200:
                    # El codigo se queda en el log, no en el stream. Al
                    # navegador le llega lo que puede hacer: reintentar.
                    logger.error('El asistente respondio %s en streaming', r.status_code)
                    yield f"data: {json.dumps({'error': 'El asistente no pudo iniciar la respuesta. Intenta de nuevo.'})}\n\n"
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

        # Conectar no salio en 10s: casi siempre es que el servicio no esta
            # levantado. El timeout de lectura es otro caso, el de "se conecta
            # y luego se queda pensando", y su mensaje tiene que ser otro para
            # que el usuario sepa si reintentar ya o esperar.
        except requests.exceptions.ConnectTimeout:
            logger.error('No se pudo conectar con el asistente en streaming')
            yield f"data: {json.dumps({'error': 'No se pudo conectar con el asistente'})}\n\n"
        except requests.exceptions.ReadTimeout:
            logger.error('El asistente dejo de enviar respuesta a mitad')
            yield f"data: {json.dumps({'error': 'El asistente se quedo pensando y se corto. Intenta de nuevo.'})}\n\n"
        except requests.exceptions.Timeout:
            logger.error("Timeout conectando al servicio")
            yield f"data: {json.dumps({'error': 'Tiempo de espera agotado'})}\n\n"
        except requests.exceptions.ConnectionError:
            logger.exception('No se pudo conectar con el microservicio de IA en streaming')
            yield f"data: {json.dumps({'error': 'No se pudo conectar con el asistente'})}\n\n"
        except Exception:
            # El log se lleva la excepcion entera; al navegador no sale
            # str(e), que antes podia filtrar la URL interna o la cabecera de
            # autenticacion.
            logger.exception('Error inesperado en streaming')
            yield f"data: {json.dumps({'error': 'Ocurrio un error inesperado al escribir la respuesta.'})}\n\n"

    response = StreamingHttpResponse(
        generar_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Connection'] = 'keep-alive'

    return response
