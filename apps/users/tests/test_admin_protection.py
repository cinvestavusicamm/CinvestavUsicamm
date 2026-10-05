"""
Fase 1: reglas de proteccion del ADMIN.

Un ADMIN no puede desactivarse ni cambiarse su propio rol, y el sistema
no puede quedarse sin ningun ADMIN activo. Las reglas viven en
UserService, no en el JS, y los rechazos se auditan.

Sobre select_for_update: en SQLite Django lo ignora en silencio, asi que
estos tests verifican la LOGICA y el rollback, no el bloqueo. El
comportamiento bajo concurrencia esta sin comprobar; el comando para
verificarlo en PostgreSQL esta en PLAN.md.
"""
import datetime
import json

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.users.config.constants import ROLE_ADMIN, ROLE_DOCENTE
from apps.users.models import BitacoraEvento, Institucion, Rol, Usuario
from apps.users.api.usuarios import editar_usuario_ajax, toggle_usuario
from apps.users.services.user_service import (
    AutoCambioRolRechazado,
    AutoDesactivacionRechazada,
    OperacionRechazada,
    SinAdminActivo,
    UserService,
)

_contador = [0]


class _BaseAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.institucion = Institucion.objects.create(
            nombre="Institucion de prueba", tipo="UNIVERSIDAD", activo=True
        )
        self.rol_admin = Rol.objects.create(nombre_rol=ROLE_ADMIN)
        self.rol_docente = Rol.objects.create(nombre_rol=ROLE_DOCENTE)

    def _crear_admin(self, activo=True):
        _contador[0] += 1
        return Usuario.objects.create(
            nombre="Admin",
            apellido_paterno="Prueba",
            correo=f"admin{_contador[0]}@test.com",
            curp=f"FASE{_contador[0]:02d}000000AAA0",
            contrasena="x",
            rol=self.rol_admin,
            institucion=self.institucion,
            activo=activo,
            fecha_registro=datetime.datetime.now(),
        )

    def _sesion_de(self, usuario):
        return self._peticion_de(usuario)

    def _peticion_de(self, usuario, data=None, url="/administrador/"):
        """Request con la sesion del usuario indicado y, opcionalmente, un
        cuerpo POST."""
        request = self.factory.post(url, data=data or {})
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_rol"] = usuario.rol.nombre_rol
        request.session.save()
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def _post_de_edicion(self, actor, objetivo, **extra):
        data = {
            "nombre": objetivo.nombre,
            "apellido_paterno": objetivo.apellido_paterno,
            "correo": objetivo.correo,
            "curp": objetivo.curp,
        }
        data.update(extra)
        url = reverse(
            "administrador:editar_usuario_ajax",
            kwargs={"id": objetivo.id_usuario},
        )
        return self._peticion_de(actor, data=data, url=url)


class ProteccionDeAdminActivoTests(_BaseAdminTest):
    # --- el ADMIN no puede consigo mismo ---------------------------------

    def test_admin_no_puede_desactivarse_a_si_mismo(self):
        admin = self._crear_admin()

        with self.assertRaises(AutoDesactivacionRechazada) as ctx:
            UserService.alternar_activo(admin.id_usuario, actor_id=admin.id_usuario)

        self.assertEqual(ctx.exception.status, 400)
        self.assertEqual(ctx.exception.codigo, "auto_desactivacion")
        admin.refresh_from_db()
        self.assertTrue(admin.activo, "el ADMIN quedo desactivado")

    def test_admin_no_puede_cambiarse_su_propio_rol(self):
        admin = self._crear_admin()

        with self.assertRaises(AutoCambioRolRechazado) as ctx:
            UserService.editar_usuario(
                admin.id_usuario,
                {"rol": self.rol_docente.id_rol},
                actor_id=admin.id_usuario,
            )

        self.assertEqual(ctx.exception.status, 400)
        admin.refresh_from_db()
        self.assertEqual(admin.rol.nombre_rol, ROLE_ADMIN)

    def test_admin_puede_cambiarse_el_nombre_pero_no_el_rol(self):
        """El bloqueo es al cambio de rol, no a editarse en general."""
        admin = self._crear_admin()

        UserService.editar_usuario(
            admin.id_usuario,
            {"nombre": "Nuevo", "rol": self.rol_admin.id_rol},
            actor_id=admin.id_usuario,
        )

        admin.refresh_from_db()
        self.assertEqual(admin.nombre, "Nuevo")
        self.assertEqual(admin.rol.nombre_rol, ROLE_ADMIN)

    # --- el ultimo ADMIN activo -----------------------------------------

    def test_no_se_puede_desactivar_al_ultimo_admin_activo(self):
        admin = self._crear_admin()

        with self.assertRaises(SinAdminActivo) as ctx:
            UserService.alternar_activo(admin.id_usuario, actor_id=None)

        self.assertEqual(ctx.exception.status, 409)
        self.assertEqual(ctx.exception.codigo, "sin_admin_activo")
        admin.refresh_from_db()
        self.assertTrue(admin.activo)

    def test_no_se_puede_quitar_el_rol_al_ultimo_admin_activo(self):
        admin = self._crear_admin()

        with self.assertRaises(SinAdminActivo):
            UserService.editar_usuario(
                admin.id_usuario, {"rol": self.rol_docente.id_rol}, actor_id=None
            )

        admin.refresh_from_db()
        self.assertEqual(admin.rol.nombre_rol, ROLE_ADMIN)

    def test_con_dos_admins_si_se_puede_desactivar_a_uno(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()

        UserService.alternar_activo(admin_b.id_usuario, actor_id=admin_a.id_usuario)

        admin_b.refresh_from_db()
        self.assertFalse(admin_b.activo)
        admin_a.refresh_from_db()
        self.assertTrue(admin_a.activo)

    def test_con_dos_admins_si_se_puede_quitar_el_rol_a_uno(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()

        UserService.editar_usuario(
            admin_b.id_usuario, {"rol": self.rol_docente.id_rol}, actor_id=admin_a.id_usuario
        )

        admin_b.refresh_from_db()
        self.assertEqual(admin_b.rol.nombre_rol, ROLE_DOCENTE)
        self.assertTrue(admin_a.__class__.objects.filter(activo=True, rol=self.rol_admin).count() == 1)

    def test_un_admin_inactivo_no_cuenta_como_administrador_activo(self):
        """El ADMIN desactivado no sostiene el sistema: hay que poder
        activar al otro sin quedarse sin ninguno."""
        admin_inactivo = self._crear_admin(activo=False)
        admin_activo = self._crear_admin()

        with self.assertRaises(SinAdminActivo):
            UserService.alternar_activo(admin_activo.id_usuario, actor_id=None)

        UserService.alternar_activo(admin_inactivo.id_usuario, actor_id=None)
        admin_inactivo.refresh_from_db()
        self.assertTrue(admin_inactivo.activo)

    def test_desactivar_a_un_docente_no_afecta_a_los_admins(self):
        admin = self._crear_admin()
        docente = Usuario.objects.create(
            nombre="Docente",
            apellido_paterno="Normal",
            correo="docente@test.com",
            curp="DOCE000000AAA00001",
            contrasena="x",
            rol=self.rol_docente,
            institucion=self.institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )

        UserService.alternar_activo(docente.id_usuario, actor_id=admin.id_usuario)

        docente.refresh_from_db()
        self.assertFalse(docente.activo)
        admin.refresh_from_db()
        self.assertTrue(admin.activo)


class ProteccionDeAdminActivoEnLasVistasTests(_BaseAdminTest):
    """Las vistas traducen el rechazo a 400/409 y dejan mensaje util."""

    def test_toggle_responde_400_al_intento_de_autodesactivacion(self):
        admin = self._crear_admin()
        request = self._sesion_de(admin)

        response = toggle_usuario(request, admin.id_usuario)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["estado"], "error")
        self.assertEqual(payload["mensaje"], "No puedes desactivar tu propia cuenta")

    def test_toggle_permitido_sobre_el_otro_admin(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._sesion_de(admin_a)

        response = toggle_usuario(request, admin_b.id_usuario)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        admin_b.refresh_from_db()
        self.assertFalse(admin_b.activo)
        admin_a.refresh_from_db()
        self.assertTrue(admin_a.activo)

    def test_el_409_de_ultimo_admin_no_es_alcanzable_desde_la_vista(self):
        """Por construccion, no por casualidad.

        Para que la vista corra, requiere_rol ya exigio que quien llama sea
        un ADMIN activo. Si el objetivo es otro ADMIN, hay al menos dos
        activos y quitar uno es legitimo. Si el objetivo es el propio
        llamante, salta antes el 400 de autodesactivacion. No queda ningun
        estado en el que esta vista pueda producir el 409.

        La regla se protege en el servicio, que es donde si se puede
        violar (llamada directa, o un futuro endpoint sin la comprobacion
        de identidad). Alli esta cubierta por
        ProteccionDeAdminActivoTests.
        """
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._sesion_de(admin_a)

        response = toggle_usuario(request, admin_b.id_usuario)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            SinAdminActivo.__name__ in str(response.content),
            "no deberia haber salto la proteccion de ultimo admin",
        )

    def test_editar_responde_400_al_cambio_de_rol_propio(self):
        admin = self._crear_admin()
        request = self._post_de_edicion(admin, admin, rol=self.rol_docente.id_rol)

        response = editar_usuario_ajax(request, admin.id_usuario)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["codigo"], "auto_cambio_rol")
        self.assertEqual(payload["error"], "No puedes cambiar tu propio rol")
        admin.refresh_from_db()
        self.assertEqual(admin.rol.nombre_rol, ROLE_ADMIN)

    def test_el_409_de_quitar_rol_tampoco_es_alcanzable_desde_la_vista(self):
        """Mismo motivo que en el toggle: el ADMIN que llama cuenta como
        administrador vivo, asi que degradar a otro nunca deja el sistema
        sin ninguno."""
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._post_de_edicion(admin_a, admin_b, rol=self.rol_docente.id_rol)

        response = editar_usuario_ajax(request, admin_b.id_usuario)

        self.assertEqual(response.status_code, 200)
        admin_b.refresh_from_db()
        self.assertEqual(admin_b.rol.nombre_rol, ROLE_DOCENTE)

    def test_editar_permitido_con_dos_admins(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._post_de_edicion(admin_a, admin_b, rol=self.rol_docente.id_rol)

        response = editar_usuario_ajax(request, admin_b.id_usuario)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        admin_b.refresh_from_db()
        self.assertEqual(admin_b.rol.nombre_rol, ROLE_DOCENTE)


class AuditoriaDeRechazosTests(_BaseAdminTest):
    """El rechazo queda registrado, y sobrevive al rollback."""

    def test_el_rechazo_por_autodesactivacion_queda_auditado(self):
        admin = self._crear_admin()
        request = self._sesion_de(admin)

        toggle_usuario(request, admin.id_usuario)

        eventos = list(BitacoraEvento.objects.filter(usuario_id=admin.id_usuario))
        tipos = [e.tipo_evento for e in eventos]
        self.assertIn("USUARIO_ACTUALIZADO_RECHAZADO", tipos)
        evento = next(e for e in eventos if e.tipo_evento == "USUARIO_ACTUALIZADO_RECHAZADO")
        self.assertEqual(evento.detalles["codigo"], "auto_desactivacion")
        self.assertEqual(evento.detalles["usuario_objetivo"], admin.id_usuario)

    def test_desactivar_al_otro_admin_no_deja_rastro_de_rechazo(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._sesion_de(admin_a)

        toggle_usuario(request, admin_b.id_usuario)

        eventos = BitacoraEvento.objects.filter(
            usuario_id=admin_a.id_usuario,
            tipo_evento="USUARIO_ACTUALIZADO_RECHAZADO",
        )
        self.assertEqual(eventos.count(), 0)

    def test_el_cambio_de_rol_propio_rechazado_queda_auditado(self):
        admin = self._crear_admin()
        request = self._post_de_edicion(admin, admin, rol=self.rol_docente.id_rol)

        editar_usuario_ajax(request, admin.id_usuario)

        eventos = BitacoraEvento.objects.filter(
            usuario_id=admin.id_usuario,
            tipo_evento="USUARIO_ACTUALIZADO_RECHAZADO",
        )
        self.assertEqual(eventos.count(), 1)
        self.assertEqual(eventos.first().detalles["codigo"], "auto_cambio_rol")

    def test_una_operacion_permitida_no_se_audita_como_rechazo(self):
        admin_a = self._crear_admin()
        admin_b = self._crear_admin()
        request = self._sesion_de(admin_a)

        response = toggle_usuario(request, admin_b.id_usuario)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            BitacoraEvento.objects.filter(
                tipo_evento="USUARIO_ACTUALIZADO_RECHAZADO"
            ).exists()
        )

    def test_el_409_conserva_su_codigo_hasta_la_capa_de_http(self):
        """El 409 no se puede disparar desde la vista, pero el camino de
        auditoria es el mismo que el del 400: _registrar_rechazo se invoca
        para cualquier OperacionRechazada, sin mirar el status. Se fija
        aqui contra el servicio para que el status no se pierda."""
        admin = self._crear_admin()

        with self.assertRaises(SinAdminActivo) as ctx:
            UserService.alternar_activo(admin.id_usuario, actor_id=None)

        self.assertEqual(ctx.exception.status, 409)
        self.assertEqual(ctx.exception.codigo, "sin_admin_activo")

    def test_el_rechazo_registrado_sobrevive_al_rollback_del_servicio(self):
        """Si el rollback del atomic se llevara por delante la escritura, el
        evento de bitacora no existiria. Es lo que fija que se registra
        fuera de la transaccion."""
        admin = self._crear_admin()
        request = self._sesion_de(admin)

        with self.assertRaises(OperacionRechazada):
            UserService.alternar_activo(admin.id_usuario, actor_id=admin.id_usuario)

        self.assertEqual(
            BitacoraEvento.objects.filter(tipo_evento="USUARIO_ACTUALIZADO_RECHAZADO").count(),
            0,
            "el servicio no debe auditar: lo hace la vista, fuera del atomic",
        )