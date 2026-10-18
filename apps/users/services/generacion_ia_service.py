"""Generacion y modificacion de la estructura de un curso con ia_service_core.

Django no habla con Ollama: le pide a ia_service_core (/api/generate-course
para crear, /api/modify-course para aplicar un cambio del chat) el JSON del
curso, lo extrae del texto que devuelve el modelo y lo valida contra el esquema
que espera el generador de cursos antes de devolverselo a la interfaz.

La validacion es de forma, no de contenido: exige que la estructura tenga
sentido (presentacion, tres bloques de modulo con sus items, examen con
preguntas y opciones), pero no cuantas preguntas trae cada quiz ni si son
exactamente cuatro opciones. Un modelo local de 3B cumple "casi" el esquema
pedido y rechazarlo entero por una pregunta de menos seria peor que dejarlo
editable, que es justo lo que hace la interfaz despues.
"""
import json
import logging

import requests
from django.conf import settings

from apps.users.services.curso_service import CursoInvalido

logger = logging.getLogger(__name__)

TIPOS_ITEM = ('video', 'quiz')


class GeneracionIAError(Exception):
    """Un fallo al generar el curso, con el codigo HTTP que le corresponde."""

    def __init__(self, mensaje, status):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def extraer_json(texto):
    """Saca el objeto JSON del texto del modelo.

    El prompt pide JSON puro, pero llama3.2:3b suele envolverlo en ```json ...
    ```. Se acepta el cerco y, como ultimo recurso, se corta del primer `{` al
    ultimo `}`. Devuelve el dict, o lanza ValueError si no hay JSON legible.
    """
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError('respuesta vacia')

    limpio = texto.strip()

    if limpio.startswith('```'):
        # ```json\n{...}\n```  ->  {...}
        partes = limpio.split('```')
        for parte in partes:
            candidato = parte
            if candidato.lstrip().lower().startswith('json'):
                candidato = candidato.lstrip()[4:]
            candidato = candidato.strip()
            if candidato.startswith('{'):
                limpio = candidato
                break

    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        # Ultimo recurso: quedarse con lo que hay entre la primera llave y la
        # ultima.
        inicio = texto.find('{')
        fin = texto.rfind('}')
        if inicio == -1 or fin <= inicio:
            raise
        return json.loads(texto[inicio:fin + 1])


def _texto_no_vacio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise CursoInvalido(f'El campo "{campo}" del curso generado esta vacio', campo)
    return valor.strip()


def _validar_pregunta(pregunta):
    if not isinstance(pregunta, dict):
        raise CursoInvalido('Cada pregunta del curso generado debe ser un objeto', 'preguntas')
    _texto_no_vacio(pregunta.get('pregunta'), 'pregunta')
    opciones = pregunta.get('opciones')
    if not isinstance(opciones, list) or len(opciones) < 2:
        raise CursoInvalido('Cada pregunta necesita al menos dos opciones', 'opciones')
    if not all(isinstance(o, str) and o.strip() for o in opciones):
        raise CursoInvalido('Las opciones deben ser texto no vacio', 'opciones')
    correcta = pregunta.get('correcta')
    if not isinstance(correcta, str) or correcta not in opciones:
        # Al modelo se le escapa a veces la respuesta correcta: la inventa o la
        # deja fuera de las opciones (visto con llama3.2:3b). No se tira el
        # curso entero por una pregunta: se marca la primera opcion, que
        # ademas es la que la interfaz pinta como correcta y deja editar.
        pregunta['correcta'] = opciones[0]


def _validar_estructura(contenido, exigir_examen=True):
    """Comprueba la forma del curso generado o lanza `CursoInvalido`.

    `exigir_examen` se pone a False al modificar: un curso de tipo "puntos" no
    tiene bloque de examen, y su JSON no debe fallar por eso. Si trae examen,
    se valida igual.
    """
    if not isinstance(contenido, dict):
        raise CursoInvalido('El curso generado no es un objeto', 'contenido')

    presentacion = contenido.get('presentacion')
    if not isinstance(presentacion, dict):
        raise CursoInvalido('El curso generado no trae presentacion', 'presentacion')
    _texto_no_vacio(presentacion.get('titulo'), 'presentacion.titulo')

    modulos = contenido.get('modulos')
    if not isinstance(modulos, list) or not modulos:
        raise CursoInvalido('El curso generado no trae modulos', 'modulos')
    # El editor del generador tiene exactamente tres bloques de modulo (los ids
    # bloque1..bloque3 son fijos): un cuarto modulo no se pintaria y se perderia
    # al guardar. Mejor rechazarlo que perderlo en silencio.
    if len(modulos) != 3:
        raise CursoInvalido('El curso tiene que tener exactamente 3 modulos', 'modulos')
    for modulo in modulos:
        if not isinstance(modulo, dict):
            raise CursoInvalido('Cada modulo debe ser un objeto', 'modulos')
        _texto_no_vacio(modulo.get('titulo'), 'modulos.titulo')
        items = modulo.get('items')
        if not isinstance(items, list):
            raise CursoInvalido('Cada modulo necesita una lista de items', 'items')
        for item in items:
            if not isinstance(item, dict) or item.get('tipo') not in TIPOS_ITEM:
                raise CursoInvalido(
                    f'Cada item debe ser de tipo {" o ".join(TIPOS_ITEM)}', 'items'
                )
            if item.get('tipo') == 'quiz':
                preguntas = item.get('preguntas')
                if not isinstance(preguntas, list) or not preguntas:
                    raise CursoInvalido('Cada quiz necesita al menos una pregunta', 'preguntas')
                for pregunta in preguntas:
                    _validar_pregunta(pregunta)

    examen = contenido.get('examen')
    if examen is None and not exigir_examen:
        examen = contenido['examen'] = {'preguntas': []}
    if not isinstance(examen, dict):
        raise CursoInvalido('El curso generado no trae examen', 'examen')
    preguntas = examen.get('preguntas')
    if not isinstance(preguntas, list):
        if exigir_examen:
            raise CursoInvalido('El examen necesita al menos una pregunta', 'examen.preguntas')
        preguntas = examen['preguntas'] = []
    if not preguntas and exigir_examen:
        raise CursoInvalido('El examen necesita al menos una pregunta', 'examen.preguntas')
    for pregunta in preguntas:
        _validar_pregunta(pregunta)

    return contenido


def _pedir_al_servicio(url, payload):
    """Una llamada al servicio de generacion. Devuelve el texto crudo del modelo."""
    try:
        respuesta = requests.post(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Internal-Service-Key': _clave(),
            },
            timeout=settings.IA_SERVICE_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise GeneracionIAError('La generacion esta tardando demasiado. Intenta de nuevo.', 504)
    except requests.exceptions.ConnectionError:
        logger.exception('No se pudo conectar con ia_service_core para generar el curso')
        raise GeneracionIAError('El generador no esta disponible. Intenta en unos momentos.', 503)

    if respuesta.status_code >= 500:
        logger.error('ia_service_core respondio %s en %s', respuesta.status_code, url)
        raise GeneracionIAError('El generador no pudo crear el curso. Intenta de nuevo.', 502)
    if respuesta.status_code == 403:
        # Clave mal puesta en el despliegue: el usuario no lo puede arreglar.
        logger.error('ia_service_core rechazo la clave interna en %s', url)
        raise GeneracionIAError('El generador no pudo crear el curso. Intenta de nuevo.', 502)
    if respuesta.status_code != 200:
        logger.error('ia_service_core respondio %s en %s', respuesta.status_code, url)
        raise GeneracionIAError('El generador devolvio una respuesta inesperada.', 502)

    try:
        datos = respuesta.json()
    except ValueError:
        logger.exception('ia_service_core devolvio algo que no es JSON')
        raise GeneracionIAError('El generador devolvio una respuesta ilegible.', 502)

    texto = datos.get('course_json')
    if not isinstance(texto, str):
        logger.error('Respuesta de %s sin "course_json": %s', url, sorted(datos))
        raise GeneracionIAError('El generador devolvio una respuesta incompleta.', 502)
    return texto


# Peticion de reparacion para el unico caso en el que se reintenta: el modelo
# contesto algo, pero sin JSON legible. No se reintenta por forma (una pregunta
# de menos), porque eso alargaria la espera y la interfaz ya deja editar.
_REPARACION = (
    '\n\nTu respuesta anterior no era JSON valido. Devuelve UNICAMENTE el objeto '
    'JSON, sin texto alrededor ni bloques de codigo.'
)


def _clave():
    from django.core.exceptions import ImproperlyConfigured

    clave = getattr(settings, 'INTERNAL_SERVICE_KEY', '') or ''
    if not clave.strip():
        raise ImproperlyConfigured(
            'INTERNAL_SERVICE_KEY no esta definida: no se puede llamar al '
            'generador de cursos. Ver .env.example.'
        )
    return clave


def _generar_y_validar(url, payload, con_reparacion, exigir_examen=True):
    """Pide el curso, extrae el JSON y lo valida, con un reintento.

    El reintento es unico y solo por JSON ilegible (el modelo contesto prosa en
    vez del objeto). Si el JSON se lee pero no tiene la forma, sube el
    `CursoInvalido`: reintentar por forma alargaria la espera sin garantia.
    """
    texto = _pedir_al_servicio(url, payload)

    try:
        return _validar_estructura(extraer_json(texto), exigir_examen=exigir_examen)
    except ValueError:
        logger.warning('La IA devolvio texto sin JSON legible; se reintenta una vez')

    texto = _pedir_al_servicio(url, con_reparacion(payload))
    try:
        return _validar_estructura(extraer_json(texto), exigir_examen=exigir_examen)
    except ValueError:
        raise GeneracionIAError('El generador no devolvio un curso valido. Intenta de nuevo.', 502)


def generar_curso_ia(peticion):
    """Devuelve el contenido de un curso generado, ya validado.

    Lanza `GeneracionIAError` (con su `status`) o `CursoInvalido` (400).
    """
    return _generar_y_validar(
        settings.IA_SERVICE_GENERATE_URL,
        {'query': peticion},
        lambda p: {'query': p['query'] + _REPARACION},
    )


def modificar_curso_ia(instruccion, contenido):
    """Aplica una instruccion del chat sobre un curso y devuelve el curso entero.

    `contenido` es el JSON del curso recogido de la pantalla; el servicio le
    pasa al modelo el curso completo y la instruccion, y devuelve el curso
    actualizado (misma forma), listo para volver a pintar.

    Lanza `GeneracionIAError` (con su `status`) o `CursoInvalido` (400).
    """
    if not isinstance(contenido, dict) or not contenido:
        raise CursoInvalido('No hay ningun curso que modificar', 'contenido')

    return _generar_y_validar(
        settings.IA_SERVICE_MODIFY_URL,
        {'instruccion': instruccion, 'contenido': contenido},
        lambda p: {**p, 'instruccion': p['instruccion'] + _REPARACION},
        exigir_examen=False,
    )
