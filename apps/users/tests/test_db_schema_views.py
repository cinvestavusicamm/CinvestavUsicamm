from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse

from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE
from apps.users.models import Institucion, Rol, Usuario

_contador = [0]


class DbSchemaViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _login_con_rol(self, rol):
        """Sesion con un usuario real del rol pedido.

        requiere_rol valida contra la base, por lo que un usuario_id = 1
        fijo ya no abre ninguna vista.
        """
        _contador[0] += 1
        institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba',
            defaults={'tipo': 'UNIVERSIDAD', 'activo': True},
        )
        rol_obj, _ = Rol.objects.get_or_create(nombre_rol=rol)
        usuario = Usuario.objects.create(
            nombre='Usuario',
            apellido_paterno='Esquema',
            correo=f'esquema{_contador[0]}@test.com',
            curp=f'ESQ{_contador[0]:02d}000000AAA0',
            contrasena='x',
            rol=rol_obj,
            institucion=institucion,
            activo=True,
            fecha_registro=datetime.now(),
        )
        session = self.client.session
        session["usuario_id"] = usuario.id_usuario
        session["usuario_rol"] = rol
        session.save()

    def test_listar_tablas_bd_requires_admin_role(self):
        self._login_con_rol(ROLE_DOCENTE)

        response = self.client.get(reverse("administrador:bd_tablas"))

        self.assertEqual(response.status_code, 403)

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
