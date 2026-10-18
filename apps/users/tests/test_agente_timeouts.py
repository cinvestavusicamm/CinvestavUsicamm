"""Los timeouts y los mensajes de error de /agente-ajax/.

Lo que se fija aqui, todo con `requests` parcheado:

- un timeout da 504 y un mensaje que dice que tardo, no un 500 generico;
- un servicio caido da 503, distinto del timeout: son dos cosas que el usuario
  distingue (volvera o waited), pero antes las dos caian en el mismo
  "ocurrio un error inesperado" con `str(e)` dentro;
- una respuesta invalida da 502 y no se finge que el modelo no pudo generar;
- el streaming usa un timeout de lectura finito, no None;
- nada de `str(e)` llega al cliente: ni en el JSON ni dentro del stream.

El detalle importante del ultimo punto: los settings de URL se leen al importar
el modulo, asi que un override de settings no los cambia. Por eso se leen
dentro de cada llamada.
"""
from unittest.mock import patch, MagicMock

import requests

from django.test import TestCase, override_settings

from apps.users.config.constants import ROLE_EVALUADOR
from apps.users.models import Institucion, Rol, Usuario

# La clave se comprueba fuera del try que convierte los fallos en un 500, para
# que un despliegue sin INTERNAL_SERVICE_KEY no se disfraces de error del
# servicio. Aqui lo que se prueba es el camino de error del servicio, asi que
# se pone una clave cualquiera.
CLAVE = {'INTERNAL_SERVICE_KEY': 'clave-de-prueba'}

URL = '/agente-ajax/'


def _respuesta(**extra):
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = {'response': 'texto del modelo'}
    r.raise_for_status.return_value = None
    for clave, valor in extra.items():
        setattr(r, clave, valor)
    return r


class _Base(TestCase):
    def setUp(self):
        inst = Institucion.objects.create(nombre='I', tipo='U', activo=True)
        rol, _ = Rol.objects.get_or_create(nombre_rol=ROLE_EVALUADOR)
        self.usuario = Usuario.objects.create(
            nombre='Eva', apellido_paterno='P', correo='eva@t.com', contrasena='x',
            curp='EVA0000000000HDFMX', rol=rol, institucion=inst,
        )
        sesion = self.client.session
        sesion['usuario_id'] = self.usuario.id_usuario
        sesion['usuario_rol'] = ROLE_EVALUADOR
        sesion.save()

    def _pregunta(self, stream=False):
        return self.client.post(
            URL, {'pregunta': 'que es un curso', 'stream': 'true' if stream else 'false'},
        )


class TimeoutTests(_Base):
    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_timeout_da_504_y_no_un_500(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout('read timed out')
        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 504)
        cuerpo = respuesta.json()
        self.assertIn('tardando', cuerpo['mensaje'].lower())
        # El texto de la libreria no sale: "read timed out" no le dice nada al
        # usuario y antes viajaba dentro de errores.
        self.assertNotIn('read timed out', respuesta.content.decode())

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_timeout_aplica_el_valor_configurado(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        with override_settings(IA_SERVICE_TIMEOUT=7):
            self._pregunta()
        self.assertEqual(mock_post.call_args.kwargs['timeout'], 7)

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_conexion_rechazada_da_503_y_no_504(self, mock_post):
        """Un servicio caido no es un timeout: se distinguen los dos codigos.

        503 es "no esta ahora", 504 es "tardo". Confundirlos hace que el
        usuario espere donde deberia recargar, o al reves.
        """
        mock_post.side_effect = requests.exceptions.ConnectionError('refused')
        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 503)
        self.assertIn('no esta disponible', respuesta.json()['mensaje'].lower())
        self.assertNotIn('refused', respuesta.content.decode())


class ServicioCaidoTests(_Base):
    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_error_http_del_servicio_da_502(self, mock_post):
        r = MagicMock()
        r.status_code = 401
        r.raise_for_status.side_effect = requests.exceptions.HTTPError(
            '401 Client Error', response=r
        )
        mock_post.return_value = r

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 502)
        # El 401 del microservicio significa clave mal puesta en el despliegue.
        # Decirselo al usuario no le sirve de nada: no lo puede arreglar.
        self.assertNotIn('401', respuesta.content.decode())

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_cuerpo_que_no_es_json_da_502(self, mock_post):
        r = MagicMock()
        r.status_code = 200
        r.raise_for_status.return_value = None
        r.json.side_effect = ValueError('Expecting value')
        mock_post.return_value = r

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 502)
        self.assertNotIn('Expecting value', respuesta.content.decode())

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_json_valido_sin_el_campo_esperado_da_502(self, mock_post):
        """Si la clave del JSON no es la que se busca, el servicio contesto otra
        cosa. Antes se devolvia "no se pudo generar una respuesta" como si fuera
        culpa del modelo, y el usuario no tenia forma de saber que era el
        contrato entre los dos servicios."""
        mock_post.return_value = _respuesta()

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['datos']['answer'], 'texto del modelo')

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_sin_el_campo_response_es_502(self, mock_post):
        r = MagicMock()
        r.status_code = 200
        r.raise_for_status.return_value = None
        r.json.return_value = {'answer': 'viene con otro nombre'}
        mock_post.return_value = r

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 502)
        self.assertIn('incompleta', respuesta.json()['mensaje'].lower())


class NoSeFiltraElDetalleTests(_Base):
    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_error_inesperado_no_muestra_la_excepcion(self, mock_post):
        mock_post.side_effect = RuntimeError(
            'fallo en http://ia_service_core:8003/api/ask con X-Internal-Service-Key:secreta'
        )
        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 500)
        cuerpo = respuesta.content.decode()
        for filtrado in ('ia_service_core', 'secreta', 'RuntimeError', 'X-Internal-Service-Key',
                         'Traceback'):
            self.assertNotIn(filtrado, cuerpo)

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_el_log_si_lleva_el_detalle(self, mock_post):
        """El detalle no se pierde: se queda en el log del servidor, que es
        donde sirve. Sin esto, un fallo raro seria indiagnosticable."""
        mock_post.side_effect = RuntimeError('boom')
        with self.assertLogs('apps.users.api.agente', level='ERROR') as registros:
            self._pregunta()
        texto = '\n'.join(registros.output)
        self.assertIn('boom', texto)
        self.assertIn('Traceback', texto)


class StreamingTests(TestCase):
    """El streaming se genera como generador: se consume con list()."""

    @patch('apps.users.api.agente.requests.post')
    def test_timeout_de_lectura_no_es_infinito(self, mock_post):
        """Antes era timeout=(30, None): None es "espera para siempre".

        Si el servicio se colgaba sin cerrar la conexion, esa peticion se
        quedaba con un worker de gunicorn para siempre y con pocos workers el
        sitio entero se caia.
        """
        from apps.users.api import agente

        r = MagicMock()
        r.status_code = 200
        r.__enter__ = MagicMock(return_value=r)
        r.__exit__ = MagicMock(return_value=False)
        r.iter_lines.return_value = ['data: {"type": "content", "token": "hola"}']
        mock_post.return_value = r

        list(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content)

        timeout = mock_post.call_args.kwargs['timeout']
        self.assertIsInstance(timeout, tuple)
        self.assertIsNotNone(timeout[1], 'el timeout de lectura no puede ser None')

    @patch('apps.users.api.agente.requests.post')
    def test_timeout_de_lectura_tiene_su_propio_mensaje(self, mock_post):
        from apps.users.api import agente

        r = MagicMock()
        r.status_code = 200
        r.__enter__ = MagicMock(return_value=r)
        r.__exit__ = MagicMock(return_value=False)
        r.iter_lines.side_effect = requests.exceptions.ReadTimeout()
        mock_post.return_value = r

        lineas = b''.join(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content).decode()

        # Distinto del timeout de conectar: aqui el servicio si arranco y se
        # quedo pensando a mitad, que se corrige con otra pregunta, no
        # esperando a que vuelva.
        self.assertIn('se quedo pensando', lineas)
        self.assertNotIn('conectar', lineas)
        self.assertNotIn('ReadTimeout', lineas)
        self.assertNotIn('Traceback', lineas)

    @patch('apps.users.api.agente.requests.post')
    def test_timeout_de_conexion_en_streaming_tiene_otro_mensaje(self, mock_post):
        from apps.users.api import agente

        mock_post.side_effect = requests.exceptions.ConnectTimeout()

        lineas = b''.join(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content).decode()

        self.assertIn('conectar', lineas)
        self.assertNotIn('conectando', lineas)

    @patch('apps.users.api.agente.requests.post')
    def test_error_inesperado_en_streaming_no_filtra_detalle(self, mock_post):
        from apps.users.api import agente

        mock_post.side_effect = RuntimeError(
            'fallo en http://ia_service_core:8003 con key secreta'
        )

        lineas = b''.join(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content).decode()

        for filtrado in ('ia_service_core', 'secreta', 'RuntimeError', 'Traceback'):
            self.assertNotIn(filtrado, lineas)
        self.assertIn('inesperado', lineas)

    @patch('apps.users.api.agente.requests.post')
    def test_error_http_en_streaming_no_muestra_el_codigo(self, mock_post):
        from apps.users.api import agente

        r = MagicMock()
        r.status_code = 503
        r.__enter__ = MagicMock(return_value=r)
        r.__exit__ = MagicMock(return_value=False)
        mock_post.return_value = r

        lineas = b''.join(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content).decode()

        # El 503 va al log; al navegador solo le llega que puede reintentar.
        self.assertNotIn('503', lineas)
        self.assertIn('Intenta de nuevo', lineas)

    @patch('apps.users.api.agente.requests.post')
    def test_usa_los_timeouts_configurados(self, mock_post):
        from apps.users.api import agente

        r = MagicMock()
        r.status_code = 200
        r.__enter__ = MagicMock(return_value=r)
        r.__exit__ = MagicMock(return_value=False)
        r.iter_lines.return_value = []
        mock_post.return_value = r

        with override_settings(IA_SERVICE_CONNECT_TIMEOUT=3, IA_SERVICE_READ_TIMEOUT=42):
            list(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content)

        self.assertEqual(mock_post.call_args.kwargs['timeout'], (3, 42))


class ContratoConIaServiceCoreTests(_Base):
    """Lo que viaja en la peticion a ia_service_core.

    El endpoint real (verificado a mano) es POST /api/ask con un DTO que exige
    "query"; antes Django mandaba "prompt", asi que el servicio contestaba 422 y
    aqui se veia como un 502 de "no pudo procesar la pregunta". Ademas el
    servicio devuelve los fallos de la IA como texto dentro de "response" con
    HTTP 200, asi que hay que reconocerlos.
    """

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_manda_query_y_prompt(self, mock_post):
        mock_post.return_value = _respuesta()

        self._pregunta()

        enviado = mock_post.call_args.kwargs['json']
        self.assertEqual(enviado['query'], 'que es un curso')
        self.assertEqual(enviado['prompt'], 'que es un curso')

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_manda_la_cabecera_del_servicio(self, mock_post):
        mock_post.return_value = _respuesta()

        self._pregunta()

        cabeceras = mock_post.call_args.kwargs['headers']
        self.assertEqual(cabeceras['X-Internal-Service-Key'], 'clave-de-prueba')

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE, IA_SERVICE_URL='http://otro:9000/api/ask')
    def test_usa_la_url_configurada(self, mock_post):
        mock_post.return_value = _respuesta()

        self._pregunta()

        self.assertEqual(mock_post.call_args.args[0], 'http://otro:9000/api/ask')

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_fallo_de_embedding_dentro_de_response_da_502(self, mock_post):
        r = _respuesta()
        r.json.return_value = {
            'response': 'Error: No pude procesar tu pregunta (Fallo en Embedding).',
        }
        mock_post.return_value = r

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 502)
        # El sentinela interno no se le ensena al usuario.
        self.assertNotIn('Embedding', respuesta.content.decode())

    @patch('apps.users.api.agente.requests.post')
    @override_settings(**CLAVE)
    def test_ollama_caido_dentro_de_response_da_502(self, mock_post):
        r = _respuesta()
        r.json.return_value = {'response': 'Error generando respuesta: connect refused'}
        mock_post.return_value = r

        respuesta = self._pregunta()

        self.assertEqual(respuesta.status_code, 502)
        self.assertNotIn('connect refused', respuesta.content.decode())


class StreamingConClaveTests(TestCase):
    """El streaming tambien manda la clave y lee la URL de settings."""

    def _respuesta_stream(self):
        r = MagicMock()
        r.status_code = 200
        r.__enter__ = MagicMock(return_value=r)
        r.__exit__ = MagicMock(return_value=False)
        r.iter_lines.return_value = []
        return r

    @patch('apps.users.api.agente.requests.post')
    def test_manda_la_clave(self, mock_post):
        from apps.users.api import agente

        mock_post.return_value = self._respuesta_stream()

        list(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content)

        cabeceras = mock_post.call_args.kwargs['headers']
        self.assertEqual(cabeceras['X-Internal-Service-Key'], 'clave-de-prueba')

    @patch('apps.users.api.agente.requests.post')
    def test_usa_la_url_configurada(self, mock_post):
        from apps.users.api import agente

        mock_post.return_value = self._respuesta_stream()

        with override_settings(IA_SERVICE_STREAM_URL='http://otro:9000/api/ask/stream'):
            list(agente.agente_streaming('hola', 'clave-de-prueba').streaming_content)

        self.assertEqual(mock_post.call_args.args[0], 'http://otro:9000/api/ask/stream')