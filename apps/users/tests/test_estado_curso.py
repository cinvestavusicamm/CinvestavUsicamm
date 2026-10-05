"""Una sola lista de estados de curso, y una funcion que normaliza variantes.

El problema que cubre esto: `Curso.estado` era un CharField sin `choices` que
se escribia desde once sitios y se leia comparando contra tres juegos de
literales distintos. El caso que mas dano hacia era la plantilla del
generador, que mandaba `'EnRevision'` (sin guion ni tilde) mientras el
evaluador escribia `'En_Revisión'`: un curso enviado a revision desde la
interfaz quedaba en un estado con el que ninguna comparacion por igualdad
encontraba nada. Los tableros no se enteraban porque cuentan con
`icontains`, de modo que el error era invisible.
"""
from django.db import migrations
from django.test import SimpleTestCase, TestCase

from apps.users.config.constants import (
    ESTADO_APROBADO,
    ESTADO_BORRADOR,
    ESTADO_EN_REVISION,
    ESTADO_INACTIVO,
    ESTADO_RECHAZADO,
    ESTADOS_CURSO,
    ESTADOS_CURSO_CHOICES,
    normalizar_estado_curso,
    reconocer_estado_curso,
)
from apps.users.models import Curso


class LaListaUnicaTests(SimpleTestCase):
    def test_los_cinco_estados_y_en_ese_orden(self):
        self.assertEqual(
            ESTADOS_CURSO,
            ('Borrador', 'En_Revisión', 'Aprobado', 'Rechazado', 'Inactivo'),
        )

    def test_las_choices_cubren_la_lista_sin_repetir(self):
        self.assertEqual([v for v, _ in ESTADOS_CURSO_CHOICES], list(ESTADOS_CURSO))
        self.assertEqual(len(ESTADOS_CURSO_CHOICES), len(ESTADOS_CURSO))

    def test_el_curso_nace_en_borrador_y_nunca_aprobado(self):
        """Regla de negocio: lo generado por IA no se aprueba solo."""
        self.assertEqual(ESTADOS_CURSO[0], ESTADO_BORRADOR)
        self.assertEqual(Curso._meta.get_field('estado').default, ESTADO_BORRADOR)


class NormalizarVariantesTests(SimpleTestCase):
    def test_las_variantes_de_revision_caen_en_la_canonica(self):
        for variante in ('EnRevision', 'En Revisión', 'en_revision', 'en-revisión', 'EN REVISIÓN'):
            with self.subTest(variante=variante):
                self.assertEqual(reconocer_estado_curso(variante), ESTADO_EN_REVISION)

    def test_las_mayusculas_y_los_espacios_no_cambian_el_estado(self):
        self.assertEqual(reconocer_estado_curso('  borrador '), ESTADO_BORRADOR)
        self.assertEqual(reconocer_estado_curso('BORRADOR'), ESTADO_BORRADOR)

    def test_los_estados_que_ya_no_existen_mapean_a_su_equivalente(self):
        """Publicado y Completado son Aprobado; Observaciones, Rechazado.

        Estas cuatro cadenas se comparaban en vistas y plantillas contra
        estados que nadie escribia, asi que esas ramas eran inalcanzables.
        """
        self.assertEqual(reconocer_estado_curso('Publicado'), ESTADO_APROBADO)
        self.assertEqual(reconocer_estado_curso('Completado'), ESTADO_APROBADO)
        self.assertEqual(reconocer_estado_curso('Observaciones'), ESTADO_RECHAZADO)
        # "Pendiente" y "Revisión" venían de la lista de validar_estado.
        self.assertEqual(reconocer_estado_curso('Pendiente'), ESTADO_EN_REVISION)
        self.assertEqual(reconocer_estado_curso('Revisión'), ESTADO_EN_REVISION)

    def test_sin_valor_se_presupone_borrador(self):
        self.assertEqual(reconocer_estado_curso(None), ESTADO_BORRADOR)
        self.assertEqual(reconocer_estado_curso(''), ESTADO_BORRADOR)
        self.assertEqual(reconocer_estado_curso('   '), ESTADO_BORRADOR)

    def test_lo_que_no_se_reconoce_devuelve_none(self):
        """None y no un valor por defecto: quien llama tiene que poder
        distinguir "no me pasaron estado" de "me pasaron uno que no conozco",
        porque lo primero es un borrador y lo segundo un error."""
        for basura in ('loquesea', 'aprobado por el jefe', 'Borrador!', '99'):
            with self.subTest(basura=basura):
                self.assertIsNone(reconocer_estado_curso(basura))

    def test_normalizar_devuelve_el_defecto_cuando_no_reconoce(self):
        self.assertEqual(normalizar_estado_curso('loquesea'), ESTADO_BORRADOR)
        self.assertEqual(normalizar_estado_curso('loquesea', ESTADO_INACTIVO), ESTADO_INACTIVO)

    def test_normalizar_no_toca_un_estado_ya_canonico(self):
        for canonico in ESTADOS_CURSO:
            with self.subTest(canonico=canonico):
                self.assertEqual(normalizar_estado_curso(canonico), canonico)

    def test_todo_estado_devuelto_esta_en_la_lista(self):
        for variante in ('EnRevision', 'Publicado', 'churro', '', 'Aprobado'):
            with self.subTest(variante=variante):
                self.assertIn(normalizar_estado_curso(variante), ESTADOS_CURSO)


class ElModeloDeclaraLasChoicesTests(SimpleTestCase):
    def test_el_campo_lleva_las_choices_de_la_constante(self):
        campo = Curso._meta.get_field('estado')
        self.assertEqual(list(campo.choices), list(ESTADOS_CURSO_CHOICES))

    def test_las_choices_siguen_siendo_texto_libre_en_la_base(self):
        """Que las choices esten no impide guardar otro valor.

        Importante porque si no, anadir las choices habria sido una migracion
        con datos, y no lo es.
        """
        self.assertTrue(Curso._meta.get_field('estado').null)


class LaMigracionNoTocaDatosTests(SimpleTestCase):
    """La migracion 0008 solo anota las choices; no convierte nada.

    Las filas que ya tuvieran un estado fuera de la lista --y hay, porque
    hasta ahora no habia lista-- tienen que seguir igual despues de migrar.
    """
    def test_la_migracion_solo_hace_un_alterfield_de_choices(self):
        import importlib

        modulo = importlib.import_module('apps.users.migrations.0008_curso_estado_choices')
        operaciones = [op for op in modulo.Migration.operations]
        self.assertEqual(len(operaciones), 1, 'la migracion deberia tener una sola operacion')

        operacion = operaciones[0]
        self.assertIsInstance(operacion, migrations.AlterField)
        self.assertEqual(operacion.model_name.lower(), 'curso')
        self.assertEqual(operacion.name, 'estado')
        self.assertEqual([v for v, _ in operacion.field.choices], list(ESTADOS_CURSO))
        # Y nada de migraciones con datos: ni RunPython ni nada que reescriba
        # la columna. Es lo que hace que aplicarla sea inocua.
        for nombre in dir(modulo.Migration):
            self.assertNotIn('RunPython', nombre)


class ValidadorDeEstadoDelegaTests(SimpleTestCase):
    def test_acepta_lo_canonico_y_las_variantes(self):
        from apps.users.validators import CursoValidator

        self.assertEqual(CursoValidator.validar_estado(ESTADO_APROBADO), ESTADO_APROBADO)
        self.assertEqual(CursoValidator.validar_estado('EnRevision'), ESTADO_EN_REVISION)

    def test_rechaza_lo_que_no_conoce(self):
        from django.core.exceptions import ValidationError

        from apps.users.validators import CursoValidator

        with self.assertRaises(ValidationError):
            CursoValidator.validar_estado('loquesea')


class NingunSitioUsaLosLiteralesViejosTests(TestCase):
    """Guardia de regresión sobre el código, no sobre los datos.

    Los lectores con `icontains` ("revision", "aprob") se dejan como estan: son
    los que hacen que un curso guardado antes de este arreglo siga contando
    en los tableros. Lo que no puede volver a aparecer es un estado escrito o
    comparado por igualdad con una variante.
    """

    LITERALES_VIEJOS = ("'EnRevision'", "'En Revisión'", "'Publicado'", "'En Progreso'", "'Activo'", "'Completado'", "'Observaciones'")

    def test_ningun_python_escribe_una_variante(self):
        import pathlib

        from django.conf import settings

        raiz = pathlib.Path(settings.BASE_DIR) / 'apps'
        ofensores = []
        for ruta in raiz.rglob('*.py'):
            if 'tests' in ruta.parts or '__pycache__' in ruta.parts:
                continue
            for numero, linea in enumerate(ruta.read_text().splitlines(), 1):
                if 'estado=' not in linea:
                    continue
                for viejo in self.LITERALES_VIEJOS:
                    if viejo in linea:
                        ofensores.append(f'{ruta.relative_to(raiz)}:{numero} {linea.strip()}')
        self.assertEqual(ofensores, [], f'estado escrito con una variante: {ofensores}')

    def test_la_plantilla_del_generador_solo_manda_estados_canonicos(self):
        """La escritura que mas dano hacia.

        La plantilla del generador es la que guardaba 'EnRevision'. Este test
        la cubre a proposito: el guard de Python y el de comparaciones no la
        alcanzan, porque es una llamada a funcion y no un `curso.estado ==`.
        """
        import pathlib
        import re

        from django.conf import settings

        ruta = pathlib.Path(settings.BASE_DIR) / 'templates' / 'generador_cursos' / 'generador_de_cursos.html'
        estados = re.findall(r"guardarCurso\(\s*'([^']+)'", ruta.read_text())
        self.assertTrue(estados, 'no se encontro ningun guardarCurso(...) en la plantilla')
        for enviado in estados:
            with self.subTest(enviado=enviado):
                self.assertIn(enviado, ESTADOS_CURSO)

    def test_el_js_no_tiene_clases_de_estados_que_no_existen(self):
        """cursos.js mapeaba estado -> clase, con 'Publicado' y sin 'Inactivo'."""
        import pathlib
        import re

        from django.conf import settings

        ruta = pathlib.Path(settings.BASE_DIR) / 'static' / 'js' / 'generador' / 'cursos.js'
        texto = ruta.read_text()
        for bloque in re.findall(r'const (?:estados|iconos) = \{(.*?)\}', texto, re.S):
            for clave in re.findall(r"'([^']+)':", bloque):
                with self.subTest(clave=clave):
                    self.assertIn(clave, ESTADOS_CURSO, f'clase o icono para un estado inexistente: {clave}')

    def test_ninguna_plantilla_compara_una_variante(self):
        import pathlib

        from django.conf import settings

        raiz = pathlib.Path(settings.BASE_DIR) / 'templates'
        ofensores = []
        for ruta in raiz.rglob('*.html'):
            for numero, linea in enumerate(ruta.read_text().splitlines(), 1):
                if 'curso.estado' not in linea:
                    continue
                for viejo in self.LITERALES_VIEJOS:
                    if viejo in linea:
                        ofensores.append(f'{ruta.relative_to(raiz)}:{numero}')
        self.assertEqual(ofensores, [], f'plantilla comparando una variante: {ofensores}')