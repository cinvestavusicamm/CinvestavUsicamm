import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.models import BitacoraEvento
from apps.users.repositories import BitacoraEventoRepository
from apps.users.serializers import BitacoraEventoSerializer

@requiere_rol(ROLE_EVALUADOR)
def calendario(request):
    """
    Vista del calendario para el evaluador.
    Muestra fechas importantes y procesos del usuario.
    Usa BitacoraEvento para gestionar eventos personales.
    """
    context = VistasBdService.contexto_evaluador(request)
    usuario_id = request.session.get('usuario_id')
    eventos_recientes = BitacoraEventoRepository.get_by_usuario(usuario_id, 64) if usuario_id else []
    context['eventos_bd'] = BitacoraEventoSerializer.to_list(eventos_recientes)
    return render(request, 'Evaluador/calendario.html', context)

@requiere_rol(ROLE_EVALUADOR)
@require_http_methods(['GET', 'POST'])
def eventos_calendario_api(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=403)

    if request.method == 'GET':
        eventos = BitacoraEventoRepository.get_by_usuario(usuario_id, 64)
        return JsonResponse({
            'eventos': BitacoraEventoSerializer.to_list(eventos)
        })

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=403)

    titulo = payload.get('title') or payload.get('titulo') or 'Evento'
    tipo = payload.get('tipo') or 'evento'
    descripcion = payload.get('descripcion', '')
    lugar = payload.get('lugar', '')
    start = payload.get('start')
    end = payload.get('end')
    all_day = payload.get('allDay', False)

    if not start:
        return JsonResponse({'error': 'Campo start es obligatorio'}, status=400)

    try:
        fecha_evento = datetime.fromisoformat(start)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

    detalles = {
        'titulo': titulo,
        'lugar': lugar,
        'end': end,
        'allDay': all_day,
    }

    evento = BitacoraEvento.objects.create(
        usuario_id=usuario_id,
        tipo_evento=tipo,
        descripcion=descripcion,
        fecha_evento=fecha_evento,
        detalles=detalles,
    )

    return JsonResponse({'success': True, 'evento': BitacoraEventoSerializer.to_dict(evento)}, status=201)
