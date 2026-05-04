import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.users.views.admin_users_views import (
    agregar_usuario_ajax,
    editar_usuario_ajax,
    obtener_usuario_ajax,
    toggle_usuario,
)
from apps.users.views.auth_views import sesion


def _attach_session_and_messages(request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    setattr(request, "_messages", FallbackStorage(request))
    return request


class AuthViewsUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("apps.users.views.auth_views.Usuario")
    def test_sesion_redirects_when_user_not_found(self, usuario_model):
        request = self.factory.post(
            reverse("sesion"),
            data={"curp": "CURP123", "password": "wrong"},
        )
        _attach_session_and_messages(request)

        usuario_model.objects.select_related.return_value.get.side_effect = (
            usuario_model.DoesNotExist
        )

        response = sesion(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("sesion"))

    @patch("apps.users.views.auth_views.timezone.now")
    @patch("apps.users.views.auth_views.Usuario")
    def test_sesion_sets_session_and_redirects_admin(self, usuario_model, now_mock):
        now_mock.return_value = "2026-01-01T00:00:00"
        fake_user = SimpleNamespace(
            activo=True,
            id_usuario=10,
            nombre="Ana",
            rol=SimpleNamespace(nombre_rol="Administrador"),
            check_password=MagicMock(return_value=True),
            save=MagicMock(),
        )
        usuario_model.objects.select_related.return_value.get.return_value = fake_user

        request = self.factory.post(
            reverse("sesion"),
            data={"curp": "CURP123", "password": "secure"},
        )
        _attach_session_and_messages(request)

        response = sesion(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("panel_admin"))
        self.assertEqual(request.session["usuario_id"], 10)
        self.assertEqual(request.session["usuario_nombre"], "Ana")
        self.assertEqual(request.session["usuario_rol"], "Administrador")
        fake_user.save.assert_called_once_with(update_fields=["ultimo_acceso"])


class UsersAjaxPermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_agregar_usuario_ajax_requires_session(self):
        request = self.factory.post(reverse("agregar_usuario_ajax"), data={})
        _attach_session_and_messages(request)

        response = agregar_usuario_ajax(request)
        payload = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["estado"], "error")
        self.assertIn("errores", payload)

    def test_toggle_usuario_blocks_self_deactivation(self):
        request = self.factory.post(reverse("toggle_usuario", kwargs={"id": 9}))
        _attach_session_and_messages(request)
        request.session["usuario_id"] = 9

        response = toggle_usuario(request, 9)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["estado"], "error")
        self.assertEqual(payload["mensaje"], "No puedes desactivar tu propia cuenta")


class UsersAjaxCrudTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("apps.users.views.admin_users_views.Usuario")
    def test_obtener_usuario_ajax_returns_user_data(self, usuario_model):
        fake_user = SimpleNamespace(
            id_usuario=7,
            nombre="Luis",
            apellido_paterno="Perez",
            apellido_materno="Lopez",
            correo="luis@test.com",
            curp="PEPL900101HDFRRS01",
            rol=SimpleNamespace(id_rol=2),
            institucion=SimpleNamespace(id_institucion=3),
        )
        usuario_model.objects.get.return_value = fake_user

        request = self.factory.get(reverse("obtener_usuario_ajax", kwargs={"id": 7}))
        _attach_session_and_messages(request)
        request.session["usuario_id"] = 1

        response = obtener_usuario_ajax(request, 7)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["estado"], "ok")
        self.assertEqual(payload["datos"]["id_usuario"], 7)
        self.assertEqual(payload["datos"]["correo"], "luis@test.com")

    @patch("apps.users.views.admin_users_views.Usuario")
    def test_obtener_usuario_ajax_returns_not_found(self, usuario_model):
        usuario_model.objects.get.side_effect = usuario_model.DoesNotExist

        request = self.factory.get(reverse("obtener_usuario_ajax", kwargs={"id": 999}))
        _attach_session_and_messages(request)
        request.session["usuario_id"] = 1

        response = obtener_usuario_ajax(request, 999)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["estado"], "error")
        self.assertEqual(payload["mensaje"], "Usuario no encontrado")

    @patch("apps.users.views.admin_users_views.Usuario")
    def test_editar_usuario_ajax_updates_user_data(self, usuario_model):
        fake_user = SimpleNamespace(
            nombre="Viejo",
            apellido_paterno="Dato",
            apellido_materno="Anterior",
            correo="old@test.com",
            curp="OLDCURP",
            contrasena="hash",
            save=MagicMock(),
        )
        usuario_model.objects.get.return_value = fake_user

        request = self.factory.post(
            reverse("editar_usuario_ajax", kwargs={"id": 5}),
            data={
                "nombre": "Nuevo",
                "apellido_paterno": "Apellido",
                "apellido_materno": "Materno",
                "correo": "nuevo@test.com",
                "curp": "CURPVALIDA12345678",
            },
        )
        _attach_session_and_messages(request)
        request.session["usuario_id"] = 1

        response = editar_usuario_ajax(request, 5)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["estado"], "ok")
        self.assertEqual(fake_user.nombre, "Nuevo")
        fake_user.save.assert_called_once()

    def test_editar_usuario_ajax_requires_post(self):
        request = self.factory.get(reverse("editar_usuario_ajax", kwargs={"id": 5}))
        _attach_session_and_messages(request)
        request.session["usuario_id"] = 1

        response = editar_usuario_ajax(request, 5)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["estado"], "error")
        self.assertEqual(payload["mensaje"], "Método no permitido")
