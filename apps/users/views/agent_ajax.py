import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
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
        return agente_streaming(request, pregunta)
    
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

def agente_streaming(request, pregunta):
    """Vista para streaming de respuestas"""
    
    def generar_stream():
        try:
            # Usar FASTAPI_STREAM_URL en lugar de construir la URL
            with requests.post(
                FASTAPI_STREAM_URL,  # Cambiado: usar la constante directamente
                json={"prompt": pregunta},  # Enviar como prompt para compatibilidad
                stream=True,
                timeout=180
            ) as r:
                
                for line in r.iter_lines():
                    if line:
                        try:
                            line_str = line.decode('utf-8')
                            # Reenviar la línea exactamente como viene
                            yield f"{line_str}\n"
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
    return response