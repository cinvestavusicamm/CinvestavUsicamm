class IAError(Exception):
    """Fallo de la IA que no es un error de quien pregunta.

    Existe para que el fallo no viaje como texto dentro de una respuesta 200.
    Antes, el adaptador de Ollama capturaba la excepcion y devolvia una cadena
    ("Error generando respuesta: ...") que el router empaquetaba en un 200: el
    consumidor no tenia forma de distinguir una respuesta del modelo de un
    servicio caido (ver DEUDA-12 en PLAN.md).

    El mensaje es para el log, no para el usuario: el router lo traduce a un
    codigo HTTP y un texto generico.
    """


class EmbeddingError(IAError):
    """No se pudo calcular el embedding de la consulta."""


class GenerationError(IAError):
    """El modelo no devolvio texto utilizable."""


class CourseGenerationError(GenerationError):
    """La IA no devolvio el JSON del curso."""
