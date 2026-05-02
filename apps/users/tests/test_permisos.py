from django.test import TestCase, Client
from django.urls import reverse
from apps.users.models import Usuario, Rol, Institucion
from apps.users.constants import ROLE_DOCENTE, ROLE_ADMIN, ROLE_EVALUADOR
from apps.users.services.permisos import requiere_rol
from django.http import HttpResponse
from django.shortcuts import redirect

class RequiereRolDecoratorTest(TestCase):
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        
        # Crear institución
        self.institucion = Institucion.objects.create(
            nombre="Instituto Prueba",
            codigo="INST001"
        )
        
        # Crear roles
        self.rol_docente = Rol.objects.create(
            nombre=ROLE_DOCENTE,
            descripcion="Rol de docente"
        )
        self.rol_admin = Rol.objects.create(
            nombre=ROLE_ADMIN,
            descripcion="Rol de administrador"
        )
        
        # Crear usuarios
        self.docente = Usuario.objects.create(
            nombre="Juan",
            apellido_paterno="Pérez",
            correo="juan@test.com",
            contrasena="12345",
            curp="PEXJ900101HDFRNN09",
            rol=self.rol_docente,
            institucion=self.institucion
        )
        
        self.admin = Usuario.objects.create(
            nombre="Admin",
            apellido_paterno="User",
            correo="admin@test.com",
            contrasena="12345",
            curp="USEADM900101HDFRNN09",
            rol=self.rol_admin,
            institucion=self.institucion
        )
    
    def test_decorador_sin_sesion(self):
        """Prueba que sin sesión redirige a login"""
        @requiere_rol(ROLE_DOCENTE)
        def vista_protegida(request):
            return HttpResponse("Acceso permitido")
        
        # Simular petición sin sesión
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/test/')
        
        response = vista_protegida(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('sesion', response.url)
    
    def test_decorador_con_sesion_rol_permitido(self):
        """Prueba que con sesión y rol permitido otorga acceso"""
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/test/')
        request.session = {
            'usuario_id': self.docente.id_usuario,
            'usuario_rol': ROLE_DOCENTE
        }
        
        response = vista_docente(request)
        self.assertEqual(response.status_code, 200)
    
    def test_decorador_rol_no_permitido(self):
        """Prueba que rechaza roles no permitidos"""
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/test/')
        request.session = {
            'usuario_id': self.admin.id_usuario,
            'usuario_rol': ROLE_ADMIN
        }
        
        response = vista_docente(request)
        self.assertEqual(response.status_code, 302)
    
    def test_decorador_multiples_roles_permitidos(self):
        """Prueba que permite acceso con múltiples roles"""
        @requiere_rol(ROLE_DOCENTE, ROLE_ADMIN)
        def vista_multi_rol(request):
            return HttpResponse("Acceso permitido")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/test/')
        request.session = {
            'usuario_id': self.admin.id_usuario,
            'usuario_rol': ROLE_ADMIN
        }
        
        response = vista_multi_rol(request)
        self.assertEqual(response.status_code, 200)