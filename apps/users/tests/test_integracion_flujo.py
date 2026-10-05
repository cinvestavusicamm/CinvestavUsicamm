import datetime

from django.test import TestCase, Client, override_settings
from unittest.mock import patch

from apps.users.config.constants import (
    ROLE_DOCENTE,
    ROLE_EVALUADOR,
    ROLE_GENERADOR,
)
from apps.users.models import Institucion, Rol, Usuario


class _SesionRealTest(TestCase):
    """Base con usuarios de verdad.

    Poner session['usuario_id'] = 1 a pelo solo funcionaba porque
    requiere_rol confiaba en la cookie. Ahora lo relee de la base, asi que
    un id que no existe deja la sesion vacia y la vista responde 302.
    """

    def setUp(self):
        self.client = Client()
        self.institucion = Institucion.objects.create(
            nombre="Institucion de prueba", tipo="UNIVERSIDAD", activo=True
        )
        self.roles = {}

    def _rol(self, nombre):
        if nombre not in self.roles:
            self.roles[nombre] = Rol.objects.create(nombre_rol=nombre)
        return self.roles[nombre]

    def _login_como(self, rol):
        usuario = Usuario.objects.create(
            nombre="Usuario",
            apellido_paterno="Flujo",
            correo=f"{rol.lower()}@test.com",
            curp=f"FLUJ{abs(hash(rol)) % 10 ** 12:012d}",
            contrasena="x",
            rol=self._rol(rol),
            institucion=self.institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )
        session = self.client.session
        session["usuario_id"] = usuario.id_usuario
        session["usuario_rol"] = rol
        session.save()
        return usuario


class FlujoCompletoTest(_SesionRealTest):

    # ✅ TEST AGENTE
    @override_settings(INTERNAL_SERVICE_KEY="clave-de-prueba-flujo")
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.api.agente.requests.post")
    def test_agente_ajax(self, mock_post, mock_decidir):
        # Mockear RouterService para que devuelva "agente"
        mock_decidir.return_value = "agente"

        # Mockear respuesta del servicio de IA
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"response": "Respuesta de prueba"}
        mock_response.raise_for_status = lambda: None

        # /agente-ajax/ admite ADMIN y EVALUADOR; se prueba con EVALUADOR
        # para que la lista multiple de roles quede ejercitada.
        self._login_como(ROLE_EVALUADOR)

        response = self.client.post(
            '/agente-ajax/',
            {
                'pregunta': 'hola'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST DOCENTE
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_docente_ajax(self, mock_post, mock_decidir):
        # Mockear RouterService para que devuelva "agente"
        mock_decidir.return_value = "agente"

        # Mockear respuesta del servicio de IA
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"response": "Respuesta de prueba"}
        mock_response.raise_for_status = lambda: None

        self._login_como(ROLE_DOCENTE)

        response = self.client.post(
            '/docente/ajax/',
            {
                'pregunta': '¿Cuáles son los cursos disponibles?'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST EVALUADOR
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.evaluador_ajax.requests.post")
    def test_evaluador_ajax(self, mock_post, mock_decidir):
        # Mockear RouterService para que devuelva "agente"
        mock_decidir.return_value = "agente"

        # Mockear respuesta del servicio de IA
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"response": "Respuesta de prueba"}
        mock_response.raise_for_status = lambda: None

        self._login_como(ROLE_EVALUADOR)

        response = self.client.post(
            '/evaluador/ajax/',
            {
                'pregunta': '¿Cómo evaluar un curso?'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST GENERADOR
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.generador_ajax.requests.post")
    def test_generador_ajax(self, mock_post, mock_decidir):
        # Mockear RouterService para que devuelva "agente"
        mock_decidir.return_value = "agente"

        # Mockear respuesta del servicio de IA
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"response": "Respuesta de prueba"}
        mock_response.raise_for_status = lambda: None

        self._login_como(ROLE_GENERADOR)

        response = self.client.post(
            '/generador/ajax/',
            {
                'pregunta': 'Generar un curso de matemáticas'
            }
        )

        self.assertEqual(response.status_code, 200)