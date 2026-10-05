ROLE_ADMIN = "ADMIN"
ROLE_DOCENTE = "DOCENTE"
ROLE_EVALUADOR = "EVALUADOR"
ROLE_GENERADOR = "GENERADOR"

# ---------------------------------------------------------------------------
# Estados de un curso
# ---------------------------------------------------------------------------
# Una sola lista y en un solo sitio. Antes de este bloque el estado de un
# curso se escribia desde once sitios distintos y se leia comparando contra
# otros tres juegos de literales, asi que un curso guardado como "EnRevision"
# (sin guion ni tilde, que es lo que mandaba la plantilla del generador) era
# invisible para cualquier comparacion contra el valor canonico y se colaba
# sin ruido en el conteo de los tableros, que.count() por "revision".
ESTADO_BORRADOR = 'Borrador'
ESTADO_EN_REVISION = 'En_Revisión'
ESTADO_APROBADO = 'Aprobado'
ESTADO_RECHAZADO = 'Rechazado'
ESTADO_INACTIVO = 'Inactivo'

ESTADOS_CURSO = (
    ESTADO_BORRADOR,
    ESTADO_EN_REVISION,
    ESTADO_APROBADO,
    ESTADO_RECHAZADO,
    ESTADO_INACTIVO,
)

ESTADOS_CURSO_CHOICES = tuple((estado, estado) for estado in ESTADOS_CURSO)


def _clave_de_estado(valor):
    """Reduce un estado a una clave comparable: sin tildes, espacios ni guiones.

    "En Revisión", "en_revision", "EnRevision" y "EN-REVISIÓN" tienen que
    acabar en la misma clave, que es justo lo que nunca pasaron.
    """
    import unicodedata

    texto = str(valor).strip().lower()
    # Quita lo que separa palabras: espacios, guiones y guiones bajos.
    for separador in (' ', '_', '-'):
        texto = texto.replace(separador, '')
    # Descompone y descarta los diacriticos, dejando la 'n' de "revision".
    descompuesto = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in descompuesto if unicodedata.category(c) != 'Mn')


# Variantes que ya pueden estar guardadas en la base, con su destino canonico.
# Los lectores que usan icontains ("revision", "aprob") siguen contando estas
# filas, asi que normalizar no es urgente, pero sirve para no rechazar un curso
# legitimo por un guion de mas.
_VARIANTES_ESTADO_CURSO = {
    _clave_de_estado(ESTADO_BORRADOR): ESTADO_BORRADOR,
    _clave_de_estado(ESTADO_EN_REVISION): ESTADO_EN_REVISION,
    _clave_de_estado(ESTADO_APROBADO): ESTADO_APROBADO,
    _clave_de_estado(ESTADO_RECHAZADO): ESTADO_RECHAZADO,
    _clave_de_estado(ESTADO_INACTIVO): ESTADO_INACTIVO,
    # Variantes historicas que aparecen en el codigo y en datos viejos.
    _clave_de_estado('EnRevision'): ESTADO_EN_REVISION,
    _clave_de_estado('En Revisión'): ESTADO_EN_REVISION,
    _clave_de_estado('Revisión'): ESTADO_EN_REVISION,
    _clave_de_estado('revision'): ESTADO_EN_REVISION,
    _clave_de_estado('Pendiente'): ESTADO_EN_REVISION,
    # "Publicado" lo usaba la vista del docente; un curso publicado es un curso
    # aprobado, que es el estado que de verdad existe.
    _clave_de_estado('Publicado'): ESTADO_APROBADO,
    _clave_de_estado('Completado'): ESTADO_APROBADO,
    # "Observaciones" solo aparecia en una rama de plantilla que nunca podia
    # ser cierta; el estado real al que se llega es Rechazado.
    _clave_de_estado('Observaciones'): ESTADO_RECHAZADO,
}


def normalizar_estado_curso(valor, defecto=ESTADO_BORRADOR):
    """Devuelve el estado canonico de `valor`, o `defecto` si no hay ninguno.

    Devolver `None` cuando el valor no se reconoce a proposito: quien llama
    tiene que poder distinguir "no me pasaron estado" de "me pasaron un estado
    que no conozco", porque lo segundo es un 400 y lo primero un Borrador.
    Para eso `reconocer_estado_curso` deja pasar el `None`.
    """
    estado = reconocer_estado_curso(valor)
    return defecto if estado is None else estado


def reconocer_estado_curso(valor):
    """Como `normalizar_estado_curso`, pero devuelve None si no reconoce el valor.

    None y la cadena vacia si tienen estado: un curso sin estado es un
    borrador, que es lo que dice el default del modelo.
    """
    if valor is None or not str(valor).strip():
        return ESTADO_BORRADOR
    return _VARIANTES_ESTADO_CURSO.get(_clave_de_estado(valor))
