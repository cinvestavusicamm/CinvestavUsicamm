import json

from django.core.exceptions import ValidationError

from apps.users.config.constants import (
    ESTADO_BORRADOR,
    ESTADO_INACTIVO,
    ESTADOS_CURSO,
    reconocer_estado_curso,
)
from apps.users.models import Curso, Usuario


def _docente_existe(usuario_id):
    """El docente tiene que existir de verdad antes de crear el curso.

    Sin esto, un `usuario_id` de sesion caducado produce un `IntegrityError` de
    clave foranea en el `INSERT`, que es el mismo 500 feo que se queria evitar.
    """
    return Usuario.objects.filter(id_usuario=usuario_id).exists()


class CursoInvalido(ValidationError):
    """Un dato de un curso que no vale, con el campo que lo hizo fallar.

    Hereda de `ValidationError` para que las vistas puedan convertirlo en un
    400 con el campo concreto en lugar de dejar que reviente el modelo con un
    `IntegrityError` dentro de un 500.

    El mensaje se compone pensando en lo que ve el usuario final: dice qué
    campo y qué límite, y no lleva nombres de tabla, columnas ni rutas, porque
    va a acabar en el cuerpo de la respuesta.
    """

    def __init__(self, mensaje, campo):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo


class CursoService:

    # Los límites salen del modelo. `titulo` es el max_length del CharField;
    # `descripcion` y `contenido` no tienen ninguno, asi que son una decisión
    # de este servicio.
    TITULO_MAX = Curso._meta.get_field('titulo').max_length  # 200
    DESCRIPCION_MAX = 20_000
    CONTENIDO_MAX_BYTES = 1_000_000  # 1 MB de JSON

    @staticmethod
    def obtener_cursos_docente(usuario_id):
        return Curso.objects.filter(
            docente_id=usuario_id
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_cursos_institucion(institucion_id):
        return Curso.objects.none()

    @staticmethod
    def obtener_cursos_ciclo_escolar(ciclo_escolar):
        return Curso.objects.none()

    @staticmethod
    def obtener_curso_por_id(curso_id):
        return Curso.objects.get(id_curso=curso_id)

    @staticmethod
    def _validar_titulo(titulo):
        if titulo is None:
            raise CursoInvalido('El titulo del curso es obligatorio', 'titulo')
        if not isinstance(titulo, str):
            raise CursoInvalido('El titulo del curso debe ser texto', 'titulo')
        if not titulo.strip():
            raise CursoInvalido('El titulo del curso no puede estar vacio', 'titulo')
        if len(titulo) > CursoService.TITULO_MAX:
            raise CursoInvalido(
                f'El titulo no puede pasar de {CursoService.TITULO_MAX} caracteres '
                f'(lleva {len(titulo)})',
                'titulo',
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        # None y '' son validos: el campo es null=True y las vistas pasan ''
        # cuando el formulario va vacio.
        if descripcion is None:
            return
        if not isinstance(descripcion, str):
            raise CursoInvalido('La descripcion debe ser texto', 'descripcion')
        if len(descripcion) > CursoService.DESCRIPCION_MAX:
            raise CursoInvalido(
                f'La descripcion no puede pasar de '
                f'{CursoService.DESCRIPCION_MAX} caracteres (lleva '
                f'{len(descripcion)})',
                'descripcion',
            )

    @staticmethod
    def _validar_estado(estado):
        """Normaliza a un estado canonico, o explica cual se recibio.

        `reconocer_estado_curso` devuelve None para lo que no conoce, y None es
        justo el valor por el que hay que distinguir "no me pasaron estado" de
        "me pasaron uno que no existe".
        """
        canonico = reconocer_estado_curso(estado)
        if canonico is None:
            raise CursoInvalido(
                f'El estado "{estado}" no es valido. Usa uno de: '
                f'{", ".join(ESTADOS_CURSO)}',
                'estado',
            )
        return canonico

    @staticmethod
    def _validar_docente(docente_id):
        if docente_id is None:
            raise CursoInvalido('No se sabe que usuario es el docente', 'docente')
        if not _docente_existe(docente_id):
            raise CursoInvalido('El docente indicado no existe', 'docente')

    @staticmethod
    def validar_contenido(contenido):
        """Comprueba el contenido y lo devuelve, o lanza `CursoInvalido`.

        Publica a proposito: la vista tiene que poder validar el contenido
        *antes* de crear la fila. Si creara primero y fallara despues, el
        curso quedaria en la base con un 400 en la cara del usuario, que es
        peor que no crear nada.
        """
        return CursoService._validar_contenido(contenido)

    @staticmethod
    def _validar_contenido(contenido):
        """Tope sobre el JSON serializado.

        Se mide el texto y no el numero de claves porque lo que se guarda es el
        texto: un bloque con diez campos de texto corto pesa mas que diez
        bloques vacios y es lo que puede reventar una fila.
        """
        if contenido is None:
            return {}
        if not isinstance(contenido, dict):
            raise CursoInvalido('El contenido del curso debe ser un objeto', 'contenido')
        try:
            medido = len(json.dumps(contenido, ensure_ascii=False).encode('utf-8'))
        except (TypeError, ValueError):
            raise CursoInvalido('El contenido del curso no es serializable', 'contenido')
        if medido > CursoService.CONTENIDO_MAX_BYTES:
            raise CursoInvalido(
                f'El contenido del curso no puede pasar de '
                f'{CursoService.CONTENIDO_MAX_BYTES // 1000} KB (lleva '
                f'{medido // 1000} KB)',
                'contenido',
            )
        return contenido

    @staticmethod
    def crear_curso(titulo, descripcion=None, docente_id=None, estado=ESTADO_BORRADOR, generado_con_ia=False):
        """Crea un curso tras validar. Lanza `CursoInvalido` si algo no vale.

        Todo lo que se valida aqui se valida antes de tocar la base, que es lo
        que evita el `IntegrityError` con su 500 y su `str(e)` lleno del
        esquema de la base.
        """
        CursoService._validar_titulo(titulo)
        CursoService._validar_descripcion(descripcion)
        CursoService._validar_docente(docente_id)
        estado = CursoService._validar_estado(estado)

        return Curso.objects.create(
            titulo=titulo.strip(),
            descripcion=descripcion,
            docente_id=docente_id,
            estado=estado,
            generado_con_ia=bool(generado_con_ia),
            version=1,
        )

    @staticmethod
    def guardar_contenido(curso, contenido):
        """Asigna `contenido_json` con el mismo tope de tamano.

        Va aparte de `crear_curso` porque el contenido llega despues: las vistas
        crean la fila y luego la rellenan con lo que venia en el payload.
        """
        validado = CursoService._validar_contenido(contenido)
        curso.contenido_json = validado
        curso.save(update_fields=['contenido_json', 'updated_at'])
        return curso

    @staticmethod
    def actualizar_curso(curso_id, titulo=None, descripcion=None, estado=None):
        """Actualiza lo que se le pase, validando antes de escribir.

        Se valida antes de asignar para que un fallo no deje la fila a medias en
        memoria: si el titulo es malo, el estado no llega a tocarse.
        """
        curso = CursoService.obtener_curso_por_id(curso_id)

        if titulo is not None:
            CursoService._validar_titulo(titulo)
            curso.titulo = titulo.strip()
        if descripcion is not None:
            CursoService._validar_descripcion(descripcion)
            curso.descripcion = descripcion
        if estado is not None:
            curso.estado = CursoService._validar_estado(estado)

        curso.save()
        return curso

    @staticmethod
    def desactivar_curso(curso_id):
        curso = CursoService.obtener_curso_por_id(curso_id)
        curso.estado = ESTADO_INACTIVO
        curso.save(update_fields=["estado"])
        return curso

    @staticmethod
    def obtener_total_cursos_activos():
        return Curso.objects.all().count()
