import datetime
import json

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
from apps.users.models import Institucion, Rol, Usuario
from apps.users.services.permisos import requiere_rol


class RequiereRolDecoratorTest(TestCase):
    """El decorador decide contra la base, no contra lo que dice la cookie.

    Los tests usan usuarios reales a proposito: con un id inventado el
    decorador no podria distinguir "no existe" de "no autorizado".
    """

    def setUp(self):
        self.factory = RequestFactory()
        self._contador = 0
        self.institucion = Institucion.objects.create(
            nombre='Institucion de prueba',
            tipo='UNIVERSIDAD',
            activo=True,
        )

    def _crear_usuario(self, rol=ROLE_DOCENTE, activo=True):
        self._contador += 1
        rol_obj, _ = Rol.objects.get_or_create(nombre_rol=rol)
        return Usuario.objects.create(
            nombre='Usuario',
            apellido_paterno=f'Permisos{self._contador}',
            correo=f'permisos{self._contador}@test.com',
            curp=f'PERM{self._contador:02d}000000AAA0',
            contrasena='x',
            rol=rol_obj,
            institucion=self.institucion,
            activo=activo,
            fecha_registro=datetime.datetime.now(),
        )

    def _request_con_sesion(self, usuario, url="/test/", ajax=False, sesion_rol=None):
        """Request con sesion real en base (no un dict plano)."""
        request = self.factory.get(url, headers={"x-requested-with": "XMLHttpRequest"} if ajax else {})
        request.session = self.client.session
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_rol"] = sesion_rol if sesion_rol is not None else usuario.rol.nombre_rol
        request.session.save()
        return request

    # --- sesion ausente ---------------------------------------------------

    def test_decorador_sin_sesion(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_protegida(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/")
        request.session = self.client.session

        response = vista_protegida(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)

    def test_decorador_sin_sesion_ajax_devuelve_401(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_protegida(request):
            return HttpResponse("Acceso permitido")

        request = self.factory.get("/test/", headers={"x-requested-with": "XMLHttpRequest"})
        request.session = self.client.session

        response = vista_protegida(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)["estado"], "error")

    # --- sesion vigente ---------------------------------------------------

    def test_decorador_con_sesion_rol_permitido(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_DOCENTE)
        response = vista_docente(self._request_con_sesion(usuario))

        self.assertEqual(response.status_code, 200)

    def test_decorador_multiples_roles_permitidos(self):
        @requiere_rol(ROLE_DOCENTE, ROLE_ADMIN)
        def vista_multi_rol(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        response = vista_multi_rol(self._request_con_sesion(usuario))

        self.assertEqual(response.status_code, 200)

    def test_decorador_autoriza_contra_el_rol_actual_en_base(self):
        """Sesion firmada como ADMIN: si en base ya no es ADMIN, no entra."""
        @requiere_rol(ROLE_ADMIN)
        def vista_admin(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_DOCENTE)
        response = vista_admin(self._request_con_sesion(usuario, sesion_rol=ROLE_ADMIN))

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)

    # --- rol insuficiente (403, la sesion sigue viva) ---------------------

    def test_decorador_rol_no_permitido(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        response = vista_docente(self._request_con_sesion(usuario))

        self.assertEqual(response.status_code, 403)

    def test_decorador_rol_no_permitido_devuelve_json_en_ajax(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        response = vista_docente(self._request_con_sesion(usuario, ajax=True))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.content)["estado"], "error")

    # --- sesion invalida: se invalida y se vuelve al login -----------------

    def test_usuario_borrado_con_sesion_viva(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_DOCENTE)
        request = self._request_con_sesion(usuario)
        usuario.delete()

        response = vista_docente(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)
        self.assertNotIn("usuario_id", request.session)

    def test_usuario_desactivado_con_sesion_viva(self):
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_DOCENTE)
        request = self._request_con_sesion(usuario)
        usuario.activo = False
        usuario.save(update_fields=["activo"])

        response = vista_docente(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)
        self.assertNotIn("usuario_id", request.session)

    def test_rol_cambiado_con_sesion_viva(self):
        """Degradado de ADMIN a DOCENTE: la cookie dice ADMIN, la base no."""
        @requiere_rol(ROLE_ADMIN)
        def vista_admin(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        request = self._request_con_sesion(usuario)
        nuevo_rol, _ = Rol.objects.get_or_create(nombre_rol=ROLE_DOCENTE)
        usuario.rol = nuevo_rol
        usuario.save(update_fields=["rol"])

        response = vista_admin(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("sesion", response.url)
        self.assertNotIn("usuario_id", request.session)

    def test_sesion_invalida_ajax_devuelve_401(self):
        @requiere_rol(ROLE_ADMIN)
        def vista_admin(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        request = self._request_con_sesion(usuario, ajax=True)
        usuario.delete()

        response = vista_admin(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.content)["estado"], "error")

    def test_rol_no_permitido_no_invalida_la_sesion(self):
        """403 es falta de permiso, no sesion invalida: no debe cerrar la sesion."""
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_ADMIN)
        request = self._request_con_sesion(usuario)

        vista_docente(request)

        self.assertIn("usuario_id", request.session)

    # --- coste en queries --------------------------------------------------

    def test_verificar_rol_cuesta_una_sola_consulta(self):
        """Contrato de rendimiento: el select_related deja el rol en la misma
        fila, asi que releer la identidad del usuario debe ser 1 query, no 2.
        """
        @requiere_rol(ROLE_DOCENTE)
        def vista_docente(request):
            return HttpResponse("Acceso permitido")

        usuario = self._crear_usuario(ROLE_DOCENTE)
        request = self._request_con_sesion(usuario)

        with self.assertNumQueries(1):
            response = vista_docente(request)

        self.assertEqual(response.status_code, 200)