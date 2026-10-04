"""Tests de seguridad de las acciones de administracion de usuarios.

Se ejecutan con enforce_csrf_checks=True para comprobar de verdad la
proteccion CSRF, algo que con el cliente por defecto de Django no se ejercita.

Dos detalles del orden real de las capas que condicionan las aserciones:

1. CsrfViewMiddleware actua antes que el decorador de la vista. Por eso un POST
   sin token se rechaza con 403 aunque no haya sesion; el redirect a login solo
   se observa cuando el POST si lleva token valido.
2. obtener_usuario_ajax responde con una forma plana (success y campos sueltos),
   no con el sobre de api_response.respuesta_ok.
"""

import re
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from apps.users.config.constants import (
    ROLE_ADMIN,
    ROLE_DOCENTE,
    ROLE_EVALUADOR,
    ROLE_GENERADOR,
)
from apps.users.models import Institucion, Rol, Usuario

CSRF_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


class AdminSecurityTestBase(TestCase):
    ROLES_NO_ADMIN = (ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR)

    def setUp(self):
        # La bitacora se parchea porque la migracion 0003 creo bitacora_eventos
        # sin las columnas ip_direccion ni detalles que el modelo declara, de
        # modo que escribir en ella revienta con OperationalError sobre una base
        # construida desde migraciones. Es una incongruencia de esquema aparte,
        # ajena a lo que estos tests cubren.
        patcher = patch("apps.users.api.usuarios._registrar_bitacora")
        self.registrar = patcher.start()
        self.addCleanup(patcher.stop)

        self.institucion = Institucion.objects.create(
            nombre="Instituto de prueba", tipo="INSTITUCION", activo=True
        )
        self.rol_admin = Rol.objects.create(nombre_rol=ROLE_ADMIN)
        for nombre in self.ROLES_NO_ADMIN:
            Rol.objects.create(nombre_rol=nombre)

        self.admin = self._crear("admin", self.rol_admin)
        self.docente = self._crear("docente", Rol.objects.get(nombre_rol=ROLE_DOCENTE))
        self.objetivo = self._crear("objetivo", self.rol_admin)

        self.url_agregar = reverse("administrador:agregar_usuario_ajax")
        self.url_editar = reverse("administrador:editar_usuario_ajax", kwargs={"id": self.docente.id_usuario})
        self.url_obtener = reverse("administrador:obtener_usuario_ajax", kwargs={"id": self.docente.id_usuario})
        self.url_toggle = reverse("administrador:toggle_usuario", kwargs={"id": self.docente.id_usuario})
        self.url_panel = reverse("administrador:panel_admin")
        self.url_crear_admin = reverse("administrador:crear_admin")

    def _crear(self, prefijo, rol):
        """rol puede ser un nombre o una instancia de Rol."""
        if not isinstance(rol, Rol):
            rol = Rol.objects.get(nombre_rol=rol)
        curp = f"{prefijo.upper()[:8]:<8}0000000000A"[:18]
        return Usuario.objects.create(
            nombre="Usuario",
            apellido_paterno="Prueba",
            correo=f"{prefijo}@ejemplo.mx",
            curp=curp,
            contrasena="pbkdf2_sha256$x",
            rol=rol,
            institucion=self.institucion,
            activo=True,
        )

    def _cliente(self, usuario=None, enforce_csrf=True):
        cliente = Client(enforce_csrf_checks=enforce_csrf)
        if usuario is not None:
            sesion = cliente.session
            sesion["usuario_id"] = usuario.id_usuario
            sesion["usuario_rol"] = usuario.rol.nombre_rol
            sesion.save()
        return cliente

    def _token_csrf(self, cliente):
        """Token del panel, que es lo que hacen los formularios del navegador."""
        html = cliente.get(self.url_panel).content.decode()
        return CSRF_RE.search(html).group(1)

    def _acciones(self):
        return [
            ("get", self.url_obtener, {}),
            ("post", self.url_agregar, {}),
            ("post", self.url_editar, {"id": self.docente.id_usuario}),
            ("post", self.url_toggle, {}),
            ("get", self.url_panel, {}),
            ("get", self.url_crear_admin, {}),
        ]


class AnonimoRedirectTests(AdminSecurityTestBase):
    def test_get_sin_sesion_redirige_al_login(self):
        cliente = self._cliente()

        for url in (self.url_obtener, self.url_panel, self.url_crear_admin):
            with self.subTest(url=url):
                respuesta = cliente.get(url)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(reverse("sesion"), respuesta.url)

    def test_post_sin_sesion_llega_al_decorador_y_redirige(self):
        """Se desactiva el chequeo CSRF para aislar la capa de autorizacion.

        Un usuario sin sesion no puede alcanzar el panel, asi que no hay token
        que exista. El rechazo por CSRF se cubre en test_post_sin_sesion_y_sin_token.
        """
        cliente = self._cliente(enforce_csrf=False)

        for url, datos in [
            (self.url_agregar, {}),
            (self.url_editar, {"id": self.docente.id_usuario}),
            (self.url_toggle, {}),
        ]:
            with self.subTest(url=url):
                respuesta = cliente.post(url, datos)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(reverse("sesion"), respuesta.url)

    def test_post_sin_sesion_y_sin_token_lo_corta_el_csrf(self):
        """El middleware actua antes que el decorador: 403, no 302."""
        cliente = self._cliente()

        respuesta = cliente.post(self.url_toggle, {})

        self.assertEqual(respuesta.status_code, 403)


class RolInsuficienteTests(AdminSecurityTestBase):
    def test_rol_no_admin_recibe_403_en_lectura(self):
        for rol in self.ROLES_NO_ADMIN:
            with self.subTest(rol=rol):
                usuario = self._crear(f"u{rol}", rol)
                cliente = self._cliente(usuario)

                for url in (self.url_obtener, self.url_panel, self.url_crear_admin):
                    with self.subTest(url=url):
                        self.assertEqual(cliente.get(url).status_code, 403)

    def test_rol_no_admin_recibe_403_en_escritura(self):
        """Sin token, para aislar la autorizacion: el CSRF se prueba aparte."""
        for rol in self.ROLES_NO_ADMIN:
            with self.subTest(rol=rol):
                usuario = self._crear(f"w{rol}", rol)
                cliente = self._cliente(usuario, enforce_csrf=False)

                for url, datos in [
                    (self.url_agregar, {}),
                    (self.url_editar, {"id": self.docente.id_usuario}),
                    (self.url_toggle, {}),
                ]:
                    with self.subTest(url=url):
                        self.assertEqual(cliente.post(url, datos).status_code, 403)

    def test_403_en_json_cuando_el_cliente_lo_pide(self):
        cliente = self._cliente(self.docente)

        respuesta = cliente.get(self.url_obtener, headers={"x-requested-with": "XMLHttpRequest"})

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(respuesta["Content-Type"], "application/json")
        self.assertEqual(respuesta.json()["estado"], "error")

    def test_docente_no_altera_ni_consulta_a_otros(self):
        cliente = self._cliente(self.docente, enforce_csrf=False)

        editar = cliente.post(
            reverse("administrador:editar_usuario_ajax", kwargs={"id": self.objetivo.id_usuario}),
            {"id": self.objetivo.id_usuario, "nombre": "Hackeado"},
        )
        toggle = cliente.post(
            reverse("administrador:toggle_usuario", kwargs={"id": self.objetivo.id_usuario})
        )
        leer = cliente.get(
            reverse("administrador:obtener_usuario_ajax", kwargs={"id": self.objetivo.id_usuario})
        )

        self.assertEqual(editar.status_code, 403)
        self.assertEqual(toggle.status_code, 403)
        self.assertEqual(leer.status_code, 403)

        self.objetivo.refresh_from_db()
        self.assertEqual(self.objetivo.nombre, "Usuario")
        self.assertTrue(self.objetivo.activo)


class ProteccionCsrfTests(AdminSecurityTestBase):
    def test_admin_con_post_sin_token_es_rechazado(self):
        cliente = self._cliente(self.admin)

        for url, datos in [
            (self.url_agregar, {"nombre": "X"}),
            (self.url_editar, {"id": self.docente.id_usuario}),
            (self.url_toggle, {}),
        ]:
            with self.subTest(url=url):
                self.assertEqual(cliente.post(url, datos).status_code, 403)

    def test_admin_con_token_supera_el_csrf_y_falla_por_validacion(self):
        cliente = self._cliente(self.admin)
        token = self._token_csrf(cliente)

        respuesta = cliente.post(self.url_agregar, {"nombre": "", "csrfmiddlewaretoken": token})

        self.assertNotEqual(respuesta.status_code, 403)
        self.assertEqual(respuesta.status_code, 400)

    def test_get_no_requiere_csrf(self):
        cliente = self._cliente(self.admin)

        self.assertEqual(cliente.get(self.url_obtener).status_code, 200)


class AdminLegitimoTests(AdminSecurityTestBase):
    def test_admin_alcanza_el_panel(self):
        cliente = self._cliente(self.admin)

        self.assertEqual(cliente.get(self.url_panel).status_code, 200)

    def test_lectura_de_usuario_devuelve_sus_datos(self):
        cliente = self._cliente(self.admin)

        respuesta = cliente.get(self.url_obtener)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["success"])
        self.assertEqual(respuesta.json()["correo"], self.docente.correo)

    def test_desactivar_a_otro_usuario_es_permitido(self):
        cliente = self._cliente(self.admin)
        token = self._token_csrf(cliente)

        respuesta = cliente.post(
            reverse("administrador:toggle_usuario", kwargs={"id": self.objetivo.id_usuario}),
            {"csrfmiddlewaretoken": token},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.objetivo.refresh_from_db()
        self.assertFalse(self.objetivo.activo)