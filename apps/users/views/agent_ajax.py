import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

FASTAPI_URL = "http://host.docker.internal:8003/api/ask"

@csrf_exempt
def agente_ajax(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'error': 'No autorizado', 'answer': None}, status=401)

    if request.method == "POST":
        pregunta = request.POST.get('pregunta', '').strip()
        if not pregunta:
            return JsonResponse({'error': 'No se recibió pregunta', 'answer': None}, status=400)

        try:
            r = requests.post(
                FASTAPI_URL,
                json={
                    "question": pregunta,
                    "user_id": request.session.get('usuario_id'),
                    "rol": request.session.get('usuario_rol')
                },
                timeout=30
            )
            r.raise_for_status() 
            data = r.json()
            return JsonResponse({'answer': data.get('answer', 'No hubo respuesta')})

        except requests.exceptions.RequestException:
            return JsonResponse({'error': 'Agente no disponible', 'answer': None}, status=503)

    return JsonResponse({'error': 'Método no permitido', 'answer': None}, status=405)
