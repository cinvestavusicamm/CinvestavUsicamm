"""
Matriz de autorizacion de los cuatro endpoints AJAX que consumen el agente de IA.

Los cuatro comparten el mismo fallo de partida: cada uno se limitaba a mirar que
la cookie tuviera usuario_id, sin comprobar el rol, y era @csrf_exempt. Estos
tests fijan el contrato que tienen ahora:

- sin sesion            -> 302 si el cliente pide HTML, 401 JSON si pide JSON
- con sesion, rol ajeno -> 403, sin vaciar la sesion
- con el rol correcto   -> la vista se ejecuta (200)
- sin token CSRF       -> 403 antes de llegar a la vista

Lo que NO se comprueba aqui es la respuesta del microservicio: ms_ai_agent_service
no esta levantado en test, asi que requests.post va siempre mockeado. Un 500 por
NameResolutionError seria un fallo del entorno, no de la autorizacion.
"""
import datetime

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from apps.users.config.constants import (
    ROLE_ADMIN,
    ROLE_DOCENTE,
    ROLE_EVALUADOR,
    ROLE_GENERADOR,
)
from apps.users.models import Usuario, Rol, Institucion


# (endpoint, roles que lo habilitan, modulo donde vive su requests.post)
#
# /agente-ajax/ admite dos roles a proposito: ADMIN es el unico consumidor
# hoy, EVALUADOR entra si vuelve el chat del evaluador (DEUDA-5). Por eso
# los roles van en conjunto y no en un valor suelto: la mitad de los tests
# necesita saber cuales son ajenos de verdad.
CASOS = [
    ('/agente-ajax/', (ROLE_ADMIN, ROLE_EVALUADOR), 'apps.users.api.agente'),
    ('/docente/ajax/', (ROLE_DOCENTE,), 'apps.users.views.docente_ajax'),
    ('/evaluador/ajax/', (ROLE_EVALUADOR,), 'apps.users.views.evaluador_ajax'),
    ('/generador/ajax/', (ROLE_GENERADOR,), 'apps.users.views.generador_ajax'),
]

TODOS_LOS_ROLES = [ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR]


class AutorizacionAjaxTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba',
            defaults={'tipo': 'UNIVERSIDAD', 'activo': True},
        )
        self._contador = 0

    def _login_como(self, rol):
        self._contador += 1
        rol_obj, _ = Rol.objects.get_or_create(nombre_rol=rol)
        usuario = Usuario.objects.create(
            nombre='Usuario',
            apellido_paterno=f'Autorizacion{self._contador}',
            correo=f'autorizacion{self._contador}@test.com',
            curp=f'AUTOR{self._contador:02d}000000AAA0',
            contrasena='x',
            rol=rol_obj,
            institucion=self.institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )
        session = self.client.session
        session['usuario_id'] = usuario.id_usuario
        session['usuario_rol'] = rol
        session.save()
        return usuario

    def _mock_del_microservicio(self, modulo):
        """Mock de requests.post para un modulo dado.

        requests es un modulo unico, asi que parchear '<modulo>.requests.post'
        afecta a todos los que lo importan. Para estos tests da igual: cada uno
        hace un unico POST, y asi se evita un mock por endpoint.
        """
        mock_post = patch(f'{modulo}.requests.post').start()
        self.addCleanup(patch.stopall)
        mock_post.return_value.json.return_value = {'response': 'Respuesta de prueba'}
        mock_post.return_value.raise_for_status = lambda: None
        return mock_post


class SinSesionTests(AutorizacionAjaxTestBase):
    """Sin sesion no hay nada que autorizar: al login."""

    def test_peticion_html_redirige_al_login(self):
        for endpoint, _roles, _modulo in CASOS:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, {'pregunta': 'hola'})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, reverse('sesion'))

    def test_peticion_json_devuelve_401(self):
        """Con X-Requested-With el cliente espera JSON, no una redireccion.

        Sin esto, el AJAX recibe un 302 a un HTML de login y lo que en el
        navegador seria una redireccion llega al JavaScript como cuerpo vacio.
        """
        for endpoint, _roles, _modulo in CASOS:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(
                    endpoint,
                    {'pregunta': 'hola'},
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                )
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json()['estado'], 'error')


class RolEquivocadoTests(AutorizacionAjaxTestBase):
    """Con sesion pero sin el rol: 403, no redireccion.

    Es autorizacion, no autenticacion. Redirigir taparia el motivo y devolveria
    HTML donde el AJAX espera JSON.
    """

    def test_otro_rol_no_pasa(self):
        for endpoint, permitidos, _modulo in CASOS:
            for rol_ajeno in [r for r in TODOS_LOS_ROLES if r not in permitidos]:
                with self.subTest(endpoint=endpoint, rol=rol_ajeno):
                    self._login_como(rol_ajeno)
                    response = self.client.post(
                        endpoint,
                        {'pregunta': 'hola'},
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertEqual(response.json()['estado'], 'error')

    def test_un_403_no_vacia_la_sesion(self):
        """El 403 es por rol, no por sesion caduca: el usuario sigue dentro."""
        self._login_como(ROLE_GENERADOR)
        response = self.client.post(
            '/evaluador/ajax/',
            {'pregunta': 'hola'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('usuario_id', self.client.session)

    def test_no_se_gasta_el_microservicio(self):
        """El 403 tiene que ocurrir antes de la llamada saliente.

        Si el chequeo estuviera despues del POST a ms_ai_agent_service, un rol
        equivocado seguiria consumiendo el servicio aunque la respuesta fuera
        403.
        """
        mock_post = self._mock_del_microservicio('apps.users.views.evaluador_ajax')
        self._login_como(ROLE_DOCENTE)
        response = self.client.post('/evaluador/ajax/', {'pregunta': 'hola'})
        self.assertEqual(response.status_code, 403)
        mock_post.assert_not_called()


class RolCorrectoTests(AutorizacionAjaxTestBase):
    """Con el rol correcto la vista se ejecuta de verdad."""

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_el_rol_correcto_llega_a_la_vista(self, mock_decidir):
        mock_decidir.return_value = 'agente'
        for endpoint, permitidos, modulo in CASOS:
            for rol in permitidos:
                with self.subTest(endpoint=endpoint, rol=rol):
                    self.client = Client()
                    self._mock_del_microservicio(modulo)
                    self._login_como(rol)

                    response = self.client.post(endpoint, {'pregunta': 'hola'})

                    self.assertEqual(response.status_code, 200)

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_el_chatbot_de_admin_sigue_respondiendo(self, mock_decidir):
        """Caso real de uso: chatbot-admin.js, que solo carga paneladm.html.

        No es un test deauthorization, es la garantia de que endurecer
        /agente-ajax/ no rompio el unico consumidor que existe.
        """
        mock_decidir.return_value = 'agente'
        mock_post = self._mock_del_microservicio('apps.users.api.agente')
        self._login_como(ROLE_ADMIN)

        response = self.client.post('/agente-ajax/', {'pregunta': 'hola'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['datos']['answer'], 'Respuesta de prueba')
        mock_post.assert_called_once()


class TokenCsrfTests(AutorizacionAjaxTestBase):
    """El token tiene que estar disponible y se tiene que validar.

    Un @csrf_exempt previo hacia que chatbot-admin.js enviara un token que
    Django no miraba. Estos tests usan enforce_csrf_checks=True porque el
    cliente de test normal no aplica CSRF y daria verde en falso.
    """

    def setUp(self):
        super().setUp()
        self.client = Client(enforce_csrf_checks=True)

    def test_sin_token_es_403(self):
        """Sesion de ADMIN valida, pero sin token: 403 antes de la vista."""
        self._login_como(ROLE_ADMIN)
        self._mock_del_microservicio('apps.users.api.agente')

        response = self.client.post('/agente-ajax/', {'pregunta': 'hola'})

        self.assertEqual(response.status_code, 403)

    def test_con_el_token_de_paneladm_pasa(self):
        """El token sale de paneladm.html, que es donde vive el chatbot.

        Se recorre el camino real -- GET al panel, leer la cookie, POST -- en
        vez de inyectar el token a mano, para comprobar que la plantilla
        sigue emitiendo el token del que depende chatbot-admin.js.
        """
        self._login_como(ROLE_ADMIN)
        mock_post = self._mock_del_microservicio('apps.users.api.agente')

        panel = self.client.get(reverse('administrador:panel_admin'))
        self.assertEqual(panel.status_code, 200)
        self.assertIn('csrftoken', self.client.cookies)

        response = self.client.post(
            '/agente-ajax/',
            {'pregunta': 'hola'},
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
        )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()

    def test_token_equivocado_es_403(self):
        """Un token de otra sesion no sirve: es lo que hace el CSRF."""
        self._login_como(ROLE_ADMIN)
        self._mock_del_microservicio('apps.users.api.agente')

        self.client.get(reverse('administrador:panel_admin'))

        response = self.client.post(
            '/agente-ajax/',
            {'pregunta': 'hola'},
            HTTP_X_CSRFTOKEN='token-inventado',
        )

        self.assertEqual(response.status_code, 403)


class SesionInvalidaTests(AutorizacionAjaxTestBase):
    """El rol de la sesion no es fuente de verdad: se relee en la base."""

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_usuario_desactivado_401_y_sesion_vacia(self, mock_decidir):
        mock_decidir.return_value = 'agente'
        usuario = self._login_como(ROLE_ADMIN)
        self._mock_del_microservicio('apps.users.api.agente')

        usuario.activo = False
        usuario.save()

        response = self.client.post(
            '/agente-ajax/',
            {'pregunta': 'hola'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('usuario_id', self.client.session)

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_rol_cambiado_entre_sesion_y_peticion_401(self, mock_decidir):
        """Un ADMIN degradado conserva su cookie. Requiere_rol no se la cree."""
        mock_decidir.return_value = 'agente'
        usuario = self._login_como(ROLE_ADMIN)
        self._mock_del_microservicio('apps.users.api.agente')

        # Cambio de rol hecho por otra via, no por esta sesion.
        nuevo_rol, _ = Rol.objects.get_or_create(nombre_rol=ROLE_DOCENTE)
        usuario.rol = nuevo_rol
        usuario.save()

        response = self.client.post(
            '/agente-ajax/',
            {'pregunta': 'hola'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('usuario_id', self.client.session)


class SessaoCssrfEnLosTresDeRolTests(AutorizacionAjaxTestBase):
    """Los tres AJAX de ms_ai_agent_service tampoco son csrf_exempt.

    No tienen consumidor, asi que no hay pagina de la que sacar el token. Se
    comprueba solo el lado del rechazo: si alguno se hiciera csrf_exempt en el
    futuro, este test lo detecta.
    """

    def test_sin_token_es_403_en_los_tres(self):
        casos = [
            ('/docente/ajax/', ROLE_DOCENTE, 'apps.users.views.docente_ajax'),
            ('/evaluador/ajax/', ROLE_EVALUADOR, 'apps.users.views.evaluador_ajax'),
            ('/generador/ajax/', ROLE_GENERADOR, 'apps.users.views.generador_ajax'),
        ]
        for endpoint, rol, modulo in casos:
            with self.subTest(endpoint=endpoint):
                cliente = Client(enforce_csrf_checks=True)
                self._login_como(rol)
                self._mock_del_microservicio(modulo)

                response = cliente.post(endpoint, {'pregunta': 'hola'})

                self.assertEqual(response.status_code, 403)