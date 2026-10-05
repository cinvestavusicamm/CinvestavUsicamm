"""
Automated Smoke Testing for All Views
This script dynamically tests all main routes to ensure they return 200/302 (not 500/404)
"""
import datetime
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse, get_resolver
from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
from apps.users.models import Usuario, Rol, Institucion


class ViewsSmokeTest(TestCase):
    """Automated smoke testing for all views"""
    
    def setUp(self):
        self.client = Client()
        self.resolver = get_resolver()
        self._contador = 0
    
    def _login_con_rol(self, rol):
        """Crea un usuario real del rol indicado y abre sesion con el.

        Antes fijaba usuario_id = 1 a pelo. En una base de test recien
        creada no existe esa fila, y las vistas que hacen
        Usuario.objects.get(id_usuario=...) devolvian 500.
        """
        self._contador += 1
        institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba',
            defaults={'tipo': 'UNIVERSIDAD', 'activo': True},
        )
        rol_obj, _ = Rol.objects.get_or_create(nombre_rol=rol)
        usuario = Usuario.objects.create(
            nombre='Usuario',
            apellido_paterno=f'Prueba{self._contador}',
            correo=f'prueba{self._contador}@test.com',
            curp=f'PRUEBA{self._contador:02d}000000AAA0',
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
    
    def _get_all_url_patterns(self):
        """Get all URL patterns from the project"""
        patterns = []
        
        def extract_patterns(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() - recurse
                    new_prefix = prefix + str(pattern.pattern)
                    extract_patterns(pattern.url_patterns, new_prefix)
                elif hasattr(pattern, 'name') and pattern.name:
                    # This is a named URL pattern
                    patterns.append({
                        'name': pattern.name,
                        'pattern': str(pattern.pattern),
                        'prefix': prefix
                    })
        
        extract_patterns(self.resolver.url_patterns)
        return patterns
    
    def test_main_public_routes(self):
        """Test main public routes without authentication"""
        public_routes = [
            ('home', 'GET'),
            ('sesion', 'GET'),
            ('registro', 'GET'),
            ('health_check', 'GET'),
        ]
        
        for route_data in public_routes:
            route_name = route_data[0]
            method = route_data[1]
            data = route_data[2] if len(route_data) > 2 else {}
            
            with self.subTest(ruta=route_name, metodo=method):
                if method == 'GET':
                    response = self.client.get(reverse(route_name))
                else:
                    response = self.client.post(reverse(route_name), data=data)

                # 200, 302 (redirect), 405 (GET on a POST-only route) y 400/401.
                # El 500 se quitó: aceptarlo era justo lo que ocultaba los fallos.
                self.assertIn(
                    response.status_code,
                    [200, 302, 405, 400, 401],
                    f"Route {route_name} ({method}) returned {response.status_code}"
                )
    
    def test_admin_routes_with_admin_role(self):
        """Test admin routes with admin authentication"""
        self._login_con_rol(ROLE_ADMIN)
        
        admin_routes = [
            'administrador:panel_admin',
            'administrador:bd_tablas',
        ]
        
        for route_name in admin_routes:
            with self.subTest(ruta=route_name):
                response = self.client.get(reverse(route_name))
                # Allow 200 or 302 (redirect)
                self.assertIn(
                    response.status_code,
                    [200, 302],
                    f"Admin route {route_name} returned {response.status_code}"
                )
    
    def test_docente_routes_with_docente_role(self):
        """Test docente routes with docente authentication"""
        self._login_con_rol(ROLE_DOCENTE)
        
        docente_routes = [
            'Docente:index_docente',
            'Docente:perfil',
            'Docente:panel_docente',
            'Docente:cursos_promociones',
            'Docente:consultar_progreso',
            'Docente:foros',
            'Docente:promociones_docente',
        ]
        
        for route_name in docente_routes:
            with self.subTest(ruta=route_name):
                response = self.client.get(reverse(route_name))
                # Allow 200 or 302 (redirect)
                self.assertIn(
                    response.status_code,
                    [200, 302],
                    f"Docente route {route_name} returned {response.status_code}"
                )
    
    def test_evaluador_routes_with_evaluador_role(self):
        """Test evaluador routes with evaluador authentication"""
        self._login_con_rol(ROLE_EVALUADOR)
        
        evaluador_routes = [
            'evaluador:dashboard',
            'evaluador:banco_preguntas',
            'evaluador:evaluaciones',
            'evaluador:validaciones',
            'evaluador:calendario',
            'evaluador:reportes',
            'evaluador:perfil',
            'evaluador:configuracion',
        ]
        
        for route_name in evaluador_routes:
            with self.subTest(ruta=route_name):
                response = self.client.get(reverse(route_name))
                # Allow 200 or 302 (redirect)
                self.assertIn(
                    response.status_code,
                    [200, 302],
                    f"Evaluador route {route_name} returned {response.status_code}"
                )
    
    def test_generador_routes_with_generador_role(self):
        """Test generador routes with generador authentication"""
        self._login_con_rol(ROLE_GENERADOR)
        
        generador_routes = [
            'generador_cursos:index_generador',
            'generador_cursos:cursos',
            'generador_cursos:estadisticas_cursos',
            'generador_cursos:generador_de_cursos',
            'generador_cursos:perfil_generador',
        ]
        
        for route_name in generador_routes:
            with self.subTest(ruta=route_name):
                response = self.client.get(reverse(route_name))
                # Allow 200 or 302 (redirect)
                self.assertIn(
                    response.status_code,
                    [200, 302],
                    f"Generador route {route_name} returned {response.status_code}"
                )
    
    @override_settings(INTERNAL_SERVICE_KEY="clave-de-prueba-smoke")
    @patch("apps.users.api.agente.requests.post")
    @patch("apps.users.views.docente_ajax.requests.post")
    @patch("apps.users.views.evaluador_ajax.requests.post")
    @patch("apps.users.views.generador_ajax.requests.post")
    @patch("apps.users.services.router_service.RouterService.decidir")
    def test_ajax_endpoints(self, mock_decidir, mock_gen, mock_eva, mock_doc, mock_agente):
        """Test AJAX endpoints with proper authentication

        Las cuatro vistas reenvian la consulta al microservicio de IA.
        Aqui se intercepta esa llamada porque un smoke test mide que la
        ruta esta bien cableada en Django, no si el servicio de IA esta
        levantado: sin esto las cuatro devuelven 500 por NameResolution
        y el 500 hiding the real result.

        Cada endpoint se prueba con su propio rol. Antes se entraba una
        sola vez como ADMIN y se hacian las cuatro peticiones, lo que
        solo podia funcionar porque las tres vistas de rol no
        comprobaban el rol. Ahora lo comprueban, y un 403 aqui seria
        autorizacion funcionando, no una ruta mal cableada.
        """
        mock_decidir.return_value = "agente"
        for mock in (mock_agente, mock_doc, mock_eva, mock_gen):
            mock.return_value.json.return_value = {"response": "Respuesta de prueba"}
            mock.return_value.raise_for_status = lambda: None

        # Sin barra inicial estas rutas no resuelven y devuelven 404.
        ajax_endpoints = [
            ('/agente-ajax/', 'POST', {'pregunta': 'test'}, ROLE_ADMIN),
            ('/docente/ajax/', 'POST', {'pregunta': 'test'}, ROLE_DOCENTE),
            ('/evaluador/ajax/', 'POST', {'pregunta': 'test'}, ROLE_EVALUADOR),
            ('/generador/ajax/', 'POST', {'pregunta': 'test'}, ROLE_GENERADOR),
        ]

        for endpoint, method, data, rol in ajax_endpoints:
            with self.subTest(endpoint=endpoint, metodo=method):
                self._login_con_rol(rol)
                if method == 'POST':
                    response = self.client.post(endpoint, data=data)
                else:
                    response = self.client.get(endpoint)

                # 200 y 400 (peticion invalida). Sin 500 ni 403.
                self.assertIn(
                    response.status_code,
                    [200, 400],
                    f"AJAX endpoint {endpoint} returned {response.status_code}"
                )
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        api_endpoints = [
            'api_listar_foros',
            'health_check',
        ]
        
        for endpoint in api_endpoints:
            # Some endpoints require parameters, skip those for basic smoke test
            if 'usuario' in endpoint or 'actualizar' in endpoint or 'crear' in endpoint:
                continue

            with self.subTest(endpoint=endpoint):
                response = self.client.get(reverse(endpoint))
                # Allow 200, 400, 401, 404
                self.assertIn(
                    response.status_code,
                    [200, 400, 401, 404],
                    f"API endpoint {endpoint} returned {response.status_code}"
                )


class RedireccionDocenteTest(TestCase):
    """/docente/index/ ya no renderiza: redirige al panel del docente.

    Antes pedia la plantilla docente/index_docente.html, que no existe, y
    devolvia 500 con TemplateDoesNotExist.
    """

    def setUp(self):
        self.client = Client()
        institucion = Institucion.objects.create(
            nombre='Institucion de prueba', tipo='UNIVERSIDAD', activo=True)
        rol = Rol.objects.create(nombre_rol=ROLE_DOCENTE)
        self.docente = Usuario.objects.create(
            nombre='Docente',
            apellido_paterno='Prueba',
            correo='docente@test.com',
            curp='PRUEBA010000AAA0001',
            contrasena='x',
            rol=rol,
            institucion=institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )
        session = self.client.session
        session['usuario_id'] = self.docente.id_usuario
        session['usuario_rol'] = ROLE_DOCENTE
        session.save()

    def test_index_redirige_al_panel(self):
        response = self.client.get(reverse('Docente:index_docente'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('Docente:panel_docente'))

    def test_el_panel_responde_200(self):
        response = self.client.get(reverse('Docente:panel_docente'))
        self.assertEqual(response.status_code, 200)

    def test_seguir_el_indice_lleva_al_panel(self):
        """Seguir la redireccion no vuelve al indice: no hay bucle."""
        response = self.client.get(reverse('Docente:index_docente'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'docente/panel_docente.html')

    def test_anónimo_sigue_yendo_al_login(self):
        self.client.session.flush()
        response = self.client.get(reverse('Docente:index_docente'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('sesion', response.url)
