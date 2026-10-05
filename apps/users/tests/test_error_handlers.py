"""Pruebas de las redirecciones por rol de utils.error_handlers.

Estas URL estan escritas a mano en get_user_context, no salen de
reverse(). Si se cambia o se borra una ruta, el enlace del boton de las
paginas de error se queda en 404 sin que ninguna prueba lo note.
"""

from types import SimpleNamespace

from django.test import TestCase
from django.urls import Resolver404, resolve

from utils.error_handlers import get_user_context

ROLE_ADMIN = 'ADMIN'


class RedireccionesPorRolTest(TestCase):
    """Cada URL de get_user_context debe resolver a una vista real."""

    def _contexto_de(self, rol):
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=True,
                rol=rol,
                groups=SimpleNamespace(exists=lambda: False),
            )
        )
        return get_user_context(request)['redirect_url']

    def test_el_admin_apunta_a_la_url_que_existe(self):
        url = self._contexto_de(ROLE_ADMIN)
        with self.subTest(url=url):
            self.assertEqual(url, '/administrador/panel-admin/')
            try:
                resolve(url)
            except Resolver404:
                self.fail(f"get_user_context devuelve {url}, que no resuelve a ninguna vista")

    def test_todas_las_redirecciones_por_rol_resuelven(self):
        for rol in ('ADMIN', 'GENERADOR', 'DOCENTE', 'EVALUADOR'):
            url = self._contexto_de(rol)
            with self.subTest(rol=rol, url=url):
                try:
                    resolve(url)
                except Resolver404:
                    self.fail(f"el rol {rol} devuelve {url}, que no resuelve a ninguna vista")

    def test_sin_usar_autenticado_manda_a_la_sesion(self):
        request = SimpleNamespace(user=SimpleNamespace(is_authenticated=False))
        self.assertEqual(get_user_context(request)['redirect_url'], '/sesion/')

    def test_rol_desconocido_manda_al_dashboard_principal(self):
        self.assertEqual(self._contexto_de('ROL_INVENTADO'), '/dashboard/')