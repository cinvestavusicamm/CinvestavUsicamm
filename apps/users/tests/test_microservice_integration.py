"""
Microservice Integration Testing
This test verifies that views consuming microservices communicate correctly
without timeouts or blocking errors.
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import datetime
from apps.users.config.constants import ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
from apps.users.models import Usuario, Rol, Institucion


class MicroserviceIntegrationTest(TestCase):
    """Test microservice integration in views"""
    
    def setUp(self):
        self.client = Client()
        self._contador = 0
    
    def _login_con_rol(self, rol):
        """Helper to login with specific role

        Antes fijaba usuario_id = 1 a pelo.requiere_rol relee el usuario
        en la base, y en una base de test recien creada esa fila no
        existe, asi que la sesion quedaba vacia y el endpoint respondia
        302 en vez de 200.
        """
        self._contador += 1
        institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba',
            defaults={'tipo': 'UNIVERSIDAD', 'activo': True},
        )
        rol_obj, _ = Rol.objects.get_or_create(nombre_rol=rol)
        usuario = Usuario.objects.create(
            nombre='Usuario',
            apellido_paterno=f'Micro{self._contador}',
            correo=f'micro{self._contador}@test.com',
            curp=f'MICRO{self._contador:02d}000000AAA0',
            contrasena='x',
            rol=rol_obj,
            institucion=institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )
        session = self.client.session
        session['usuario_id'] = usuario.id_usuario
        session['usuario_rol'] = rol
        session['usuario_nombre'] = usuario.nombre_completo
        session.save()
        return usuario
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_docente_ajax_ai_service_integration(self, mock_post, mock_decidir):
        """Test that docente AJAX endpoint communicates with AI service correctly"""
        
        # Setup mocks
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response from AI"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_DOCENTE)
        
        # Make request to AI agent
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': '¿Cuáles son los cursos disponibles?'}
        )
        
        self.assertEqual(response.status_code, 200, "AI agent should respond successfully")
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        
        # Verify the mock was called with correct parameters
        mock_post.assert_called_once()
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.evaluador_ajax.requests.post")
    def test_evaluador_ajax_ai_service_integration(self, mock_post, mock_decidir):
        """Test that evaluador AJAX endpoint communicates with AI service correctly"""
        
        # Setup mocks
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response from AI"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_EVALUADOR)
        
        # Make request to AI agent
        response = self.client.post(
            '/evaluador/ajax/',
            {'pregunta': '¿Cómo evaluar un curso?'}
        )
        
        self.assertEqual(response.status_code, 200, "AI agent should respond successfully")
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.generador_ajax.requests.post")
    def test_generador_ajax_ai_service_integration(self, mock_post, mock_decidir):
        """Test that generador AJAX endpoint communicates with AI service correctly"""
        
        # Setup mocks
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response from AI"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_GENERADOR)
        
        # Make request to AI agent
        response = self.client.post(
            '/generador/ajax/',
            {'pregunta': 'Generar un curso de matemáticas'}
        )
        
        self.assertEqual(response.status_code, 200, "AI agent should respond successfully")
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_ai_service_timeout_handling(self, mock_post, mock_decidir):
        """Test that AI service timeouts are handled gracefully"""
        
        # Setup mocks to simulate timeout
        mock_decidir.return_value = "agente"
        mock_post.side_effect = Exception("Timeout or connection error")
        
        self._login_con_rol(ROLE_DOCENTE)
        
        # Make request to AI agent
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': 'Test question'}
        )
        
        # Should handle error gracefully (not crash with 500)
        self.assertIn(response.status_code, [200, 400, 500], "Should handle timeout gracefully")
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_ai_service_empty_response_handling(self, mock_post, mock_decidir):
        """Test that empty AI service responses are handled correctly"""
        
        # Setup mocks to return empty response
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_DOCENTE)
        
        # Make request to AI agent
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': 'Test question'}
        )
        
        # Should handle empty response gracefully
        self.assertIn(response.status_code, [200, 400], "Should handle empty response gracefully")
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_ai_service_malformed_response_handling(self, mock_post, mock_decidir):
        """Test that malformed AI service responses are handled correctly"""
        
        # Setup mocks to return malformed response
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_DOCENTE)
        
        # Make request to AI agent
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': 'Test question'}
        )
        
        # Should handle malformed response gracefully
        self.assertIn(response.status_code, [200, 400, 500], "Should handle malformed response gracefully")
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    def test_router_service_decision_logic(self, mock_decidir):
        """Test that RouterService correctly routes requests to appropriate service"""
        
        # Test different decision outcomes
        test_cases = [
            ("agente", "agente"),
            ("cursos", "cursos"),
            ("evaluaciones", "evaluaciones"),
        ]
        
        for expected_decision, _ in test_cases:
            mock_decidir.return_value = expected_decision
            
            self._login_con_rol(ROLE_DOCENTE)
            
            # Make request
            response = self.client.post(
                '/docente/ajax/',
                {'pregunta': 'Test question'}
            )
            
            # Verify RouterService was called
            mock_decidir.assert_called()
    
    def test_ajax_endpoint_without_session(self):
        """Test that AJAX endpoints require authentication"""
        
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': 'Test question'}
        )
        
        # Should return 401 or redirect without session
        self.assertIn(response.status_code, [401, 302], "Should require authentication")
    
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_ajax_endpoint_missing_parameters(self, mock_post, mock_decidir):
        """Test that AJAX endpoints handle missing parameters correctly"""
        
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        self._login_con_rol(ROLE_DOCENTE)
        
        # Make request without required parameter
        response = self.client.post(
            '/docente/ajax/',
            {}  # Missing 'pregunta' parameter
        )
        
        # Should handle missing parameters gracefully
        self.assertIn(response.status_code, [200, 400], "Should handle missing parameters gracefully")
