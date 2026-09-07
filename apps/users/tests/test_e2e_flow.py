"""
End-to-End Integration Test for User Flow
This test simulates the complete "Happy Path" of a real user:
1. Authentication and login
2. Redirection to appropriate dashboard based on role
3. Execution of main action (course creation/consultation)
4. Communication with ms_api_gateway
5. Secure logout
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE


class EndToEndFlowTest(TestCase):
    """E2E integration test for complete user flow"""
    
    def setUp(self):
        self.client = Client()
    
    @patch("apps.users.views.auth_views.Usuario")
    def test_complete_admin_user_flow(self, mock_usuario_model):
        """Test complete flow for admin user: login -> logout"""
        
        # Setup mock user
        fake_user = MagicMock()
        fake_user.id_usuario = 1
        fake_user.nombre = "Admin"
        fake_user.apellido_paterno = "Test"
        fake_user.correo = "admin@test.com"
        fake_user.rol.nombre_rol = ROLE_ADMIN
        fake_user.save = MagicMock()
        
        mock_usuario_model.objects.select_related.return_value.get.return_value = fake_user
        
        # Step 1: Login
        response = self.client.post(
            reverse('sesion'),
            data={'curp': 'GODE561231HDFRPR09', 'password': 'secure'}
        )
        
        self.assertEqual(response.status_code, 302, "Login should redirect")
        self.assertEqual(response.url, reverse('administrador:panel_admin'), "Should redirect to admin panel")
        
        # Verify session is set
        self.assertIn('usuario_id', self.client.session)
        self.assertEqual(self.client.session['usuario_id'], 1)
        self.assertEqual(self.client.session['usuario_nombre'], 'Admin')
        self.assertEqual(self.client.session['usuario_rol'], 'Administrador')
        
        # Step 2: Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302, "Logout should redirect")
        self.assertEqual(response.url, reverse('sesion'), "Should redirect to login")
        
        # Verify session is cleared
        self.assertNotIn('usuario_id', self.client.session)
    
    @patch("apps.users.views.auth_views.Usuario")
    @patch("apps.users.services.router_service.RouterService.decidir")
    @patch("apps.users.views.docente_ajax.requests.post")
    def test_complete_docente_user_flow(self, mock_post, mock_decidir, mock_usuario_model):
        """Test complete flow for docente user: login -> AI agent interaction -> logout"""
        
        # Setup mock user
        fake_user = MagicMock()
        fake_user.id_usuario = 2
        fake_user.nombre = "Docente"
        fake_user.apellido_paterno = "Test"
        fake_user.correo = "docente@test.com"
        fake_user.rol.nombre_rol = ROLE_DOCENTE
        fake_user.save = MagicMock()
        
        mock_usuario_model.objects.select_related.return_value.get.return_value = fake_user
        
        # Setup mocks for AI service
        mock_decidir.return_value = "agente"
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Respuesta de prueba del agente"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        # Step 1: Login
        response = self.client.post(
            reverse('sesion'),
            data={'curp': 'DOCE123456HDFRPR09', 'password': 'secure'}
        )
        
        self.assertEqual(response.status_code, 302, "Login should redirect")
        self.assertIn('usuario_id', self.client.session)
        self.assertEqual(self.client.session['usuario_rol'], 'Docente')
        
        # Step 2: Interact with AI agent (communication with microservices)
        response = self.client.post(
            '/docente/ajax/',
            {'pregunta': '¿Cuáles son los cursos disponibles?'}
        )
        
        self.assertEqual(response.status_code, 200, "AI agent should respond")
        self.assertIn('success', response.json())
        
        # Step 3: Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302, "Logout should redirect")
        self.assertNotIn('usuario_id', self.client.session)
    
    @patch("apps.users.views.auth_views.Usuario")
    def test_login_redirect_based_on_role(self, mock_usuario_model):
        """Test that login redirects to correct dashboard based on user role"""
        
        test_cases = [
            (ROLE_ADMIN, 'administrador:panel_admin'),
            (ROLE_DOCENTE, 'Docente:panel_docente'),
        ]
        
        for role, expected_redirect in test_cases:
            # Setup mock user with specific role
            fake_user = MagicMock()
            fake_user.id_usuario = 1
            fake_user.nombre = "Test"
            fake_user.apellido_paterno = "User"
            fake_user.correo = "test@test.com"
            fake_user.rol.nombre_rol = role
            fake_user.save = MagicMock()
            
            mock_usuario_model.objects.select_related.return_value.get.return_value = fake_user
            
            # Login
            response = self.client.post(
                reverse('sesion'),
                data={'curp': 'TEST123456HDFRPR09', 'password': 'secure'}
            )
            
            self.assertEqual(response.status_code, 302, f"Login with role {role} should redirect")
            self.assertEqual(response.url, reverse(expected_redirect), f"Should redirect to {expected_redirect}")
            
            # Clear session for next test
            self.client.session.flush()
    
    def test_unauthenticated_access_redirects_to_login(self):
        """Test that unauthenticated users are redirected to login"""
        
        protected_routes = [
            'administrador:panel_admin',
            'administrador:bd_tablas',
            'Docente:index_docente',
            'Docente:perfil',
            'evaluador:dashboard',
            'generador_cursos:index_generador',
        ]
        
        for route in protected_routes:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 302, f"Route {route} should redirect")
            self.assertIn('sesion', response.url, f"Should redirect to login page")
    
    @patch("apps.users.views.auth_views.Usuario")
    def test_invalid_credentials_shows_error(self, mock_usuario_model):
        """Test that invalid credentials show error message"""
        
        # Mock user not found
        mock_usuario_model.objects.select_related.return_value.get.side_effect = (
            mock_usuario_model.DoesNotExist
        )
        
        response = self.client.post(
            reverse('sesion'),
            data={'curp': 'INVALID123456HDFRPR09', 'password': 'wrong'}
        )
        
        self.assertEqual(response.status_code, 302, "Should redirect on invalid credentials")
        self.assertEqual(response.url, reverse('sesion'), "Should redirect back to login")
    
    def test_health_check_accessible_without_auth(self):
        """Test that health check endpoint is accessible without authentication"""
        
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200, "Health check should be accessible")
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
