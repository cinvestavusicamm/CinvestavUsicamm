"""Creacion de cursos: validacion en el servicio y 400 con el campo concreto.

`CursoService.crear_curso` era un `Curso.objects.create` sin validacion
ninguna. Las vistas leian `datos.get('titulo')`, asi que un curso sin titulo
llegaba al modelo como `None` y reventaba con un `IntegrityError` dentro de un
`except Exception` que devolvia 500 y `str(e)`: al navegador le llegaba el
nombre de la tabla y el texto exacto del error de la base de datos.

Estos tests usan filas reales y no parchean el modelo, a proposito: con
`patch('apps.users.services.curso_service.Curso')` se puede comprobar que se
llama a `objects.create` con tales argumentos, pero no que la validacion
impida nada.
"""
from django.test import TestCase
from django.urls import reverse

from apps.users.config.constants import (
    ESTADO_APROBADO,
    ESTADO_BORRADOR,
    ESTADO_EN_REVISION,
)
from apps.users.config.constants import ROLE_DOCENTE
from apps.users.models import Curso, Institucion, Rol, Usuario
from apps.users.services.curso_service import CursoService, CursoInvalido


class _FabricaDocentes:
    """Usuarios reales: rol e institucion son NOT NULL en la base.

    Los tests de abajo usan filas de verdad, no parches, justamente porque el
    fallo que cubren --un IntegrityError dentro de un 500-- solo aparece si hay
    una tabla delante.
    """

    def __init__(self):
        self.contador = 0

    def __call__(self):
        self.contador += 1
        institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba', tipo='UNIVERSIDAD', activo=True,
        )
        rol, _ = Rol.objects.get_or_create(nombre_rol=ROLE_DOCENTE)
        return Usuario.objects.create(
            nombre='Docente', apellido_paterno='Prueba',
            correo=f'docente{self.contador}@test.com',
            contrasena='x', curp=f'DOCE{self.contador:03d}000000HDFMXN',
            rol=rol, institucion=institucion,
        )


_crear_docente = _FabricaDocentes()


class ValidacionDeTituloTests(TestCase):
    def setUp(self):
        self.docente = _crear_docente()

    def crear(self, **kwargs):
        datos = {
            'titulo': 'Curso valido',
            'descripcion': 'Una descripcion',
            'docente_id': self.docente.pk,
        }
        datos.update(kwargs)
        return CursoService.crear_curso(**datos)

    def test_un_curso_valido_se_crea(self):
        curso = self.crear()
        self.assertIsNotNone(curso.pk)
        self.assertEqual(curso.estado, ESTADO_BORRADOR)

    def test_sin_titulo_no_se_crea_y_senala_el_campo(self):
        with self.assertRaises(CursoInvalido) as ctx:
            self.crear(titulo=None)
        self.assertEqual(ctx.exception.campo, 'titulo')
        self.assertEqual(Curso.objects.count(), 0)

    def test_titulo_vacio_no_se_crea(self):
        for vacio in ('', '   '):
            with self.subTest(titulo=vacio):
                with self.assertRaises(CursoInvalido) as ctx:
                    self.crear(titulo=vacio)
                self.assertEqual(ctx.exception.campo, 'titulo')

    def test_titulo_de_mas_de_200_no_se_crea(self):
        with self.assertRaises(CursoInvalido) as ctx:
            self.crear(titulo='x' * 201)
        self.assertEqual(ctx.exception.campo, 'titulo')
        self.assertEqual(Curso.objects.count(), 0)

    def test_titulo_de_exactamente_200_si_se_crea(self):
        curso = self.crear(titulo='x' * 200)
        self.assertEqual(len(curso.titulo), 200)

    def test_el_mensaje_dice_cual_es_el_limite(self):
        with self.assertRaises(CursoInvalido) as ctx:
            self.crear(titulo='x' * 201)
        self.assertIn('200', ctx.exception.mensaje)


class ValidacionDeDescripcionTests(TestCase):
    def setUp(self):
        self.docente = _crear_docente()

    def test_una_descripcion_larga_no_se_crea(self):
        with self.assertRaises(CursoInvalido) as ctx:
            CursoService.crear_curso(
                titulo='Curso', descripcion='x' * 20001,
                docente_id=self.docente.pk,
            )
        self.assertEqual(ctx.exception.campo, 'descripcion')

    def test_una_descripcion_larga_que_cabe_si_se_crea(self):
        curso = CursoService.crear_curso(
            titulo='Curso', descripcion='x' * 20000, docente_id=self.docente.pk,
        )
        self.assertEqual(len(curso.descripcion), 20000)

    def test_descripcion_none_o_ausente_no_falla(self):
        """El campo es null=True, y las vistas pasan '' cuando no hay."""
        curso = CursoService.crear_curso(
            titulo='Curso', docente_id=self.docente.pk,
        )
        self.assertIn(curso.descripcion, (None, ''))


class ValidacionDeEstadoTests(TestCase):
    def setUp(self):
        self.docente = _crear_docente()

    def crear(self, estado):
        return CursoService.crear_curso(
            titulo='Curso', docente_id=self.docente.pk, estado=estado,
        )

    def test_los_estados_canonicos_se_crean(self):
        for estado in (ESTADO_BORRADOR, ESTADO_EN_REVISION, ESTADO_APROBADO):
            with self.subTest(estado=estado):
                self.assertEqual(self.crear(estado).estado, estado)

    def test_las_variantes_se_normalizan_al_guardar(self):
        """La plantilla del generador mandaba 'EnRevision'; al guardar queda el
        canonico, sin tocar lo que ya hay en la base."""
        curso = self.crear('EnRevision')
        self.assertEqual(curso.estado, ESTADO_EN_REVISION)

    def test_un_estado_desconocido_no_se_crea_y_senala_el_campo(self):
        with self.assertRaises(CursoInvalido) as ctx:
            self.crear('loquesea')
        self.assertEqual(ctx.exception.campo, 'estado')
        self.assertEqual(Curso.objects.count(), 0)

    def test_sin_estato_nace_borrador(self):
        self.assertEqual(self.crear(None).estado, ESTADO_BORRADOR)


class ValidacionDeContenidoTests(TestCase):
    def setUp(self):
        self.docente = _crear_docente()

    def crear(self, contenido):
        curso = CursoService.crear_curso(
            titulo='Curso', docente_id=self.docente.pk,
        )
        curso.contenido_json = contenido
        curso.save()
        return curso

    def test_un_contenido_enorme_no_se_guarda(self):
        """Sin tope, un payload grande se guarda entero en cada fila.

        El limite se comprueba en `actualizar_curso` porque el contenido se
        escribe despues de crear la fila, en la propia vista.
        """
        enorme = {'bloques': [{'titulo': 'x' * 100_000} for _ in range(50)]}
        with self.assertRaises(CursoInvalido) as ctx:
            CursoService.guardar_contenido(self.crear({}), enorme)
        self.assertEqual(ctx.exception.campo, 'contenido')

    def test_un_contenido_normal_si_se_guarda(self):
        contenido = {'bloques': [{'titulo': 'tema', 'contenido': 'texto'}]}
        curso = CursoService.guardar_contenido(self.crear({}), contenido)
        self.assertEqual(curso.contenido_json, contenido)


class ActualizacionValidaTests(TestCase):
    def setUp(self):
        self.docente = _crear_docente()
        self.curso = CursoService.crear_curso(
            titulo='Curso', docente_id=self.docente.pk,
        )

    def test_actualizar_un_titulo_invalido_no_toca_la_fila(self):
        with self.assertRaises(CursoInvalido) as ctx:
            CursoService.actualizar_curso(self.curso.pk, titulo='')
        self.assertEqual(ctx.exception.campo, 'titulo')
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.titulo, 'Curso')

    def test_actualizar_un_estado_invalido_no_toca_la_fila(self):
        with self.assertRaises(CursoInvalido) as ctx:
            CursoService.actualizar_curso(self.curso.pk, estado='loquesea')
        self.assertEqual(ctx.exception.campo, 'estado')
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.estado, ESTADO_BORRADOR)

    def test_actualizar_normaliza_la_variante(self):
        resultado = CursoService.actualizar_curso(
            self.curso.pk, estado='En Revisión',
        )
        self.assertEqual(resultado.estado, ESTADO_EN_REVISION)

    def test_sin_campos_no_toca_nada(self):
        resultado = CursoService.actualizar_curso(self.curso.pk)
        self.assertEqual(resultado.estado, ESTADO_BORRADOR)
        self.assertEqual(resultado.titulo, 'Curso')


class ErrorDeValidacionEsUtilTests(TestCase):
    def test_el_error_dice_el_campo_y_no_filtra_rutas(self):
        with self.assertRaises(CursoInvalido) as ctx:
            CursoService.crear_curso(titulo=None, docente_id=1)
        mensaje = str(ctx.exception)
        self.assertIn('titulo', mensaje)
        for filtrado in ('SELECT', 'INSERT', 'cursos', 'postgres', 'Traceback'):
            self.assertNotIn(filtrado, mensaje)

    def test_es_una_excepcion_de_django_para_poder_convertirla_en_400(self):
        from django.core.exceptions import ValidationError

        self.assertTrue(issubclass(CursoInvalido, ValidationError))