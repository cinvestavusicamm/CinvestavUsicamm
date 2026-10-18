"""Generacion de la estructura de un curso con la IA.

Cubre `services/generacion_ia_service.py` (extraccion del JSON del texto del
modelo, validacion de la forma y traduccion de fallos) y el endpoint
`/generador/api/generar-curso-ia/`.

El fixture `fixtures/ia_generate_course_respuesta.json` es una respuesta real de
ia_service_core (/api/generate-course) con llama3.2:3b, guardada tal cual para
que los tests no dependan de la red ni de Ollama.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import Client, SimpleTestCase, TestCase, override_settings

from apps.users.config.constants import ROLE_ADMIN, ROLE_GENERADOR
from apps.users.models import Curso, Institucion, Rol, Usuario
from apps.users.services.curso_service import CursoInvalido
from apps.users.services.generacion_ia_service import (
    GeneracionIAError,
    extraer_json,
    generar_curso_ia,
)

FIXTURE = Path(__file__).parent / 'fixtures' / 'ia_generate_course_respuesta.json'
CLAVE = {'INTERNAL_SERVICE_KEY': 'clave-de-prueba'}
URL = '/generador/api/generar-curso-ia/'


def _contenido_valido():
    return {
        'presentacion': {'titulo': 'Curso', 'descripcion': 'd', 'duracion': '20 horas'},
        'modulos': [
            {
                'titulo': 'Módulo 1',
                'items': [
                    {'tipo': 'video'},
                    {'tipo': 'quiz', 'preguntas': [
                        {'pregunta': 'p?', 'opciones': ['a', 'b', 'c'], 'correcta': 'a'},
                    ]},
                ],
            },
        ],
        'examen': {'preguntas': [
            {'pregunta': 'q?', 'opciones': ['a', 'b'], 'correcta': 'b'},
        ]},
    }


class ExtraerJsonTests(SimpleTestCase):
    def test_json_puro(self):
        self.assertEqual(extraer_json('{"a": 1}'), {'a': 1})

    def test_envuelto_en_cerco_de_codigo(self):
        texto = '```json\n{"presentacion": {"titulo": "x"}}\n```'
        self.assertEqual(extraer_json(texto), {'presentacion': {'titulo': 'x'}})

    def test_cerco_sin_la_palabra_json(self):
        self.assertEqual(extraer_json('```\n{"a": 2}\n```'), {'a': 2})

    def test_texto_alrededor(self):
        texto = 'Aqui tienes el curso:\n{"a": 3}\nEspero que sirva.'
        self.assertEqual(extraer_json(texto), {'a': 3})

    def test_sin_json_lanza_value_error(self):
        with self.assertRaises(ValueError):
            extraer_json('lo siento, no puedo ayudarte con eso')

    def test_texto_vacio_lanza_value_error(self):
        with self.assertRaises(ValueError):
            extraer_json('   ')


class ValidacionEstructuraTests(SimpleTestCase):
    def _con_error(self, mutar, campo):
        contenido = _contenido_valido()
        mutar(contenido)
        with self.assertRaises(CursoInvalido) as ctx:
            from apps.users.services.generacion_ia_service import _validar_estructura
            _validar_estructura(contenido)
        self.assertEqual(ctx.exception.campo, campo)

    def test_valido_pasa(self):
        from apps.users.services.generacion_ia_service import _validar_estructura
        self.assertIsInstance(_validar_estructura(_contenido_valido()), dict)

    def test_sin_presentacion(self):
        self._con_error(lambda c: c.pop('presentacion'), 'presentacion')

    def test_presentacion_sin_titulo(self):
        self._con_error(lambda c: c['presentacion'].update(titulo=''), 'presentacion.titulo')

    def test_sin_modulos(self):
        self._con_error(lambda c: c.update(modulos=[]), 'modulos')

    def test_quiz_sin_preguntas(self):
        def mutar(c):
            c['modulos'][0]['items'][1]['preguntas'] = []
        self._con_error(mutar, 'preguntas')

    def test_correcta_fuera_de_las_opciones_se_normaliza(self):
        from apps.users.services.generacion_ia_service import _validar_estructura
        contenido = _contenido_valido()
        contenido['examen']['preguntas'][0]['correcta'] = 'z'

        resultado = _validar_estructura(contenido)

        pregunta = resultado['examen']['preguntas'][0]
        self.assertEqual(pregunta['correcta'], pregunta['opciones'][0])

    def test_sin_examen(self):
        self._con_error(lambda c: c.pop('examen'), 'examen')


class GenerarCursoServicioTests(SimpleTestCase):
    def _respuesta(self, datos):
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = datos
        return r

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(**CLAVE)
    def test_devuelve_el_contenido_validado_con_el_fixture_real(self, mock_post):
        mock_post.return_value = self._respuesta(json.loads(FIXTURE.read_text()))

        contenido = generar_curso_ia('un curso cualquiera')

        self.assertIn('presentacion', contenido)
        self.assertEqual(len(contenido['modulos']), 3)
        # La peticion lleva la clave interna.
        cabeceras = mock_post.call_args.kwargs['headers']
        self.assertEqual(cabeceras['X-Internal-Service-Key'], 'clave-de-prueba')

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(**CLAVE)
    def test_reintenta_una_vez_si_el_texto_no_trae_json(self, mock_post):
        primero = self._respuesta({'course_json': 'perdona, no puedo ayudarte'})
        segundo = self._respuesta({'course_json': json.dumps(_contenido_valido())})
        mock_post.side_effect = [primero, segundo]

        contenido = generar_curso_ia('peticion')

        self.assertEqual(mock_post.call_count, 2)
        self.assertIn('presentacion', contenido)

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(**CLAVE)
    def test_sin_json_tras_el_reintento_da_502(self, mock_post):
        mock_post.return_value = self._respuesta({'course_json': 'nada de json'})

        with self.assertRaises(GeneracionIAError) as ctx:
            generar_curso_ia('peticion')

        self.assertEqual(ctx.exception.status, 502)

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(**CLAVE)
    def test_servicio_caido_da_503(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError('refused')

        with self.assertRaises(GeneracionIAError) as ctx:
            generar_curso_ia('peticion')

        self.assertEqual(ctx.exception.status, 503)
        self.assertNotIn('refused', ctx.exception.mensaje)

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(**CLAVE)
    def test_timeout_da_504(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(GeneracionIAError) as ctx:
            generar_curso_ia('peticion')

        self.assertEqual(ctx.exception.status, 504)

    @patch('apps.users.services.generacion_ia_service.requests.post')
    @override_settings(INTERNAL_SERVICE_KEY='')
    def test_sin_clave_no_llama_al_servicio(self, mock_post):
        from django.core.exceptions import ImproperlyConfigured
        with self.assertRaises(ImproperlyConfigured):
            generar_curso_ia('peticion')
        mock_post.assert_not_called()


class _BaseEndpoint(TestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre='Institucion de prueba', tipo='UNIVERSIDAD', activo=True,
        )
        self.roles = {
            nombre: Rol.objects.create(nombre_rol=nombre)
            for nombre in (ROLE_GENERADOR, ROLE_ADMIN)
        }
        self.generador = self._usuario('Generador', 'gen', ROLE_GENERADOR)
        self.admin = self._usuario('Admin', 'adm', ROLE_ADMIN)

        self.cliente = Client(enforce_csrf_checks=True)
        self._iniciar(self.generador)
        self.cliente.get('/sesion/')
        self.token = self.cliente.cookies['csrftoken'].value

    def _usuario(self, nombre, clave, rol):
        return Usuario.objects.create(
            nombre=nombre, apellido_paterno='Prueba',
            correo=f'{clave}@test.com', contrasena='x',
            curp=f'{clave.upper():<4}000000HDFMXN'[:18],
            rol=self.roles[rol], institucion=self.institucion,
        )

    def _iniciar(self, usuario):
        sesion = self.cliente.session
        sesion['usuario_id'] = usuario.id_usuario
        sesion['usuario_rol'] = usuario.rol.nombre_rol
        sesion.save()

    def _post(self, cuerpo):
        return self.cliente.post(
            URL, data=json.dumps(cuerpo),
            content_type='application/json', HTTP_X_CSRFTOKEN=self.token,
        )


class EndpointGenerarCursoTests(_BaseEndpoint):
    @override_settings(**CLAVE)
    @patch('apps.users.views.generador_cursos.cursos.servicio_generar_curso_ia')
    def test_genera_y_devuelve_el_contenido(self, mock_servicio):
        mock_servicio.return_value = _contenido_valido()

        respuesta = self._post({'peticion': 'un curso'})

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertTrue(cuerpo['success'])
        self.assertIn('presentacion', cuerpo['contenido'])

    @override_settings(**CLAVE)
    @patch('apps.users.views.generador_cursos.cursos.servicio_generar_curso_ia')
    def test_peticion_vacia_da_400(self, mock_servicio):
        respuesta = self._post({'peticion': '   '})
        self.assertEqual(respuesta.status_code, 400)
        mock_servicio.assert_not_called()

    @override_settings(**CLAVE)
    @patch('apps.users.views.generador_cursos.cursos.servicio_generar_curso_ia')
    def test_fallo_del_servicio_da_su_codigo(self, mock_servicio):
        mock_servicio.side_effect = GeneracionIAError('no disponible', 503)
        respuesta = self._post({'peticion': 'un curso'})
        self.assertEqual(respuesta.status_code, 503)

    def test_sin_rol_da_403(self):
        self._iniciar(self.admin)
        respuesta = self._post({'peticion': 'un curso'})
        self.assertEqual(respuesta.status_code, 403)


class NacerBorradorTests(_BaseEndpoint):
    """Un curso generado con IA no puede nacer Aprobado."""

    @override_settings(**CLAVE)
    def test_crear_con_ia_y_aprobado_guarda_borrador(self):
        respuesta = self.cliente.post(
            '/generador/api/crear-curso-generador/',
            data=json.dumps({
                'titulo': 'Curso de prueba',
                'descripcion': 'd',
                'contenido': _contenido_valido(),
                'estado': 'Aprobado',
                'generado_con_ia': True,
            }),
            content_type='application/json', HTTP_X_CSRFTOKEN=self.token,
        )
        self.assertEqual(respuesta.status_code, 200)
        curso = Curso.objects.get(id_curso=respuesta.json()['curso_id'])
        self.assertEqual(curso.estado, 'Borrador')

    @override_settings(**CLAVE)
    def test_sin_ia_el_estado_pedido_se_respeta(self):
        respuesta = self.cliente.post(
            '/generador/api/crear-curso-generador/',
            data=json.dumps({
                'titulo': 'Curso manual',
                'descripcion': 'd',
                'estado': 'En_Revisión',
                'generado_con_ia': False,
            }),
            content_type='application/json', HTTP_X_CSRFTOKEN=self.token,
        )
        self.assertEqual(respuesta.status_code, 200)
        curso = Curso.objects.get(id_curso=respuesta.json()['curso_id'])
        self.assertEqual(curso.estado, 'En_Revisión')
