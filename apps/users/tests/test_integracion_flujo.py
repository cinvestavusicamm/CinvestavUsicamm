from django.test import TestCase, Client
from unittest.mock import patch


class FlujoCompletoTest(TestCase):

    def setUp(self):
        self.client = Client()

        # 🔥 Simular sesión
        session = self.client.session
        session['usuario_id'] = 1
        session.save()

    # ✅ TEST AGENTE
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_agente_ajax(self, mock_post, mock_decidir):
        # Mockear RouterService para que devuelva "agente"
        mock_decidir.return_value = "agente"
        
        # Mockear respuesta del servicio de IA
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"response": "Respuesta de prueba"}
        mock_response.raise_for_status = lambda: None

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

        response = self.client.post(
            '/generador/ajax/',
            {
                'pregunta': 'Generar un curso de matemáticas'
            }
        )

        self.assertEqual(response.status_code, 200)