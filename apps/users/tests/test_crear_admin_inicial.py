from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.users.config.constants import ROLE_ADMIN
from apps.users.models import Institucion, Rol, Usuario

CURP_VALIDA = "AAAAA000000AAA0001"
CURP_OCUPADA = "BBBBB000000BBB0002"


class CrearAdminInicialCommandTests(TestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre="Instituto de prueba", tipo="INSTITUCION", activo=True
        )
        self.rol_admin = Rol.objects.create(nombre_rol=ROLE_ADMIN)

    def _admin_existente(self):
        return Usuario.objects.create(
            nombre="Admin",
            apellido_paterno="Existente",
            correo="admin@existente.mx",
            curp=CURP_OCUPADA,
            contrasena="x",
            rol=self.rol_admin,
            institucion=self.institucion,
            activo=True,
        )

    def test_no_hace_nada_si_ya_existe_un_admin(self):
        self._admin_existente()

        with self.assertRaisesMessage(CommandError, "Ya existe al menos un ADMIN"):
            call_command("crear_admin_inicial")

        self.assertEqual(Usuario.objects.filter(rol=self.rol_admin).count(), 1)

    def test_crea_el_admin_con_los_datos_ingresados(self):
        with patch("builtins.input", side_effect=[
            CURP_VALIDA, "Ana", "Lopez", "-",
        ]), patch("getpass.getpass", side_effect=[
            "contrasena-segura", "contrasena-segura",
        ]):
            call_command("crear_admin_inicial", username="ana@ejemplo.mx", stdout=StringIO())

        admin = Usuario.objects.get(correo="ana@ejemplo.mx")
        self.assertEqual(admin.rol, self.rol_admin)
        self.assertEqual(admin.curp, CURP_VALIDA)
        self.assertEqual(admin.nombre, "Ana")
        self.assertEqual(admin.institucion, self.institucion)
        self.assertTrue(admin.check_password("contrasena-segura"))
        self.assertTrue(admin.activo)

    def test_rechaza_curp_invalida(self):
        with patch("builtins.input", side_effect=["curp-corta"]):
            with self.assertRaisesMessage(CommandError, "CURP solo admite letras"):
                call_command("crear_admin_inicial", username="ana@ejemplo.mx", stdout=StringIO())

        self.assertFalse(Usuario.objects.exists())

    def test_rechaza_contrasenas_que_no_coinciden(self):
        with patch("builtins.input", side_effect=[CURP_VALIDA]), patch(
            "getpass.getpass", side_effect=["contrasena-una", "contrasena-dos"]
        ):
            with self.assertRaisesMessage(CommandError, "no coinciden"):
                call_command("crear_admin_inicial", username="ana@ejemplo.mx", stdout=StringIO())

        self.assertFalse(Usuario.objects.exists())

    def test_rechaza_correo_ya_usado(self):
        Rol.objects.create(nombre_rol="DOCENTE")
        Usuario.objects.create(
            nombre="Docente",
            apellido_paterno="Repetido",
            correo="docente@ejemplo.mx",
            curp=CURP_OCUPADA,
            contrasena="x",
            rol=Rol.objects.get(nombre_rol="DOCENTE"),
            institucion=self.institucion,
            activo=True,
        )

        with self.assertRaisesMessage(CommandError, "Ya existe un usuario con el correo"):
            call_command("crear_admin_inicial", username="docente@ejemplo.mx", stdout=StringIO())

    def test_registra_la_contrasena_hasheada(self):
        with patch("builtins.input", side_effect=[
            CURP_VALIDA, "Ana", "Lopez", "-",
        ]), patch("getpass.getpass", side_effect=[
            "contrasena-segura", "contrasena-segura",
        ]):
            call_command("crear_admin_inicial", username="ana@ejemplo.mx", stdout=StringIO())

        admin = Usuario.objects.get(correo="ana@ejemplo.mx")
        self.assertNotEqual(admin.contrasena, "contrasena-segura")
        self.assertTrue(admin.contrasena.startswith("pbkdf2_"))