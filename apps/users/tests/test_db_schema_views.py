from django.test import Client, TestCase
from django.urls import reverse

from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE


class DbSchemaViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _login_con_rol(self, rol):
        session = self.client.session
        session["usuario_id"] = 1
        session["usuario_rol"] = rol
        session.save()

    def test_listar_tablas_bd_requires_admin_role(self):
        self._login_con_rol(ROLE_DOCENTE)

        response = self.client.get(reverse("administrador:bd_tablas"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("sesion"))

    def test_listar_tablas_bd_returns_html_for_admin(self):
        self._login_con_rol(ROLE_ADMIN)

        response = self.client.get(reverse("administrador:bd_tablas"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/bd_tablas.html")
        self.assertContains(response, "Tablas y atributos")

    def test_listar_tablas_bd_returns_database_schema_as_json_for_admin(self):
        self._login_con_rol(ROLE_ADMIN)

        response = self.client.get(f"{reverse('administrador:bd_tablas')}?format=json")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["estado"], "ok")
        self.assertIn("total_tablas", payload["datos"])
        self.assertIn("total_columnas", payload["datos"])
        self.assertIn("total_filas", payload["datos"])
        self.assertIn("tablas", payload["datos"])
        self.assertGreater(payload["datos"]["total_tablas"], 0)
        self.assertIn("columns", payload["datos"]["tablas"][0])
