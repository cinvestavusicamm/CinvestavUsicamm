from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE
from apps.users.services.permisos import requiere_rol


class RequiereRolDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_decorador_sin_sesion(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_protegida(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/")
        request.session = {}

        response = vista_protegida(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)

    def test_decorador_con_sesion_rol_permitido(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/")
        request.session = {"usuario_id": 1, "usuario_rol": ROLE_DOCENTE}

        response = vista_docente(request)

        self.assertEqual(response.status_code, 200)

    def test_decorador_rol_no_permitido(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/")
        request.session = {"usuario_id": 2, "usuario_rol": ROLE_ADMIN}

        response = vista_docente(request)

        self.assertEqual(response.status_code, 302)

    def test_decorador_multiples_roles_permitidos(self):
        @requiere_rol(ROLE_DOCENTE, ROLE_ADMIN)
        def vista_multi_rol(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/")
        request.session = {"usuario_id": 2, "usuario_rol": ROLE_ADMIN}

        response = vista_multi_rol(request)

        self.assertEqual(response.status_code, 200)
