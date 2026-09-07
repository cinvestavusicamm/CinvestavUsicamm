import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from apps.users.config.constants import ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_GENERADOR
from apps.users.services.router_service import RouterService
from apps.users.api.agente import agente_ajax
from apps.users.api.roles import (
    datos_docente_ajax,
    datos_evaluador_ajax,
    datos_generador_ajax,
)


def _request_with_session(request, rol):
    request.session = {"usuario_id": 1, "usuario_rol": rol}
    return request


class RouterServiceTests(SimpleTestCase):
    def test_decidir_envia_consultas_de_datos_a_bd(self):
        self.assertEqual(RouterService.decidir("cuantos cursos pendientes hay"), "bd")

    def test_decidir_envia_conversacion_general_al_agente(self):
        self.assertEqual(RouterService.decidir("ayudame a redactar una introduccion"), "agente")


class AgentAjaxRouterTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("apps.users.api.agente.RouterService.responder_desde_bd")
    def test_agente_ajax_usa_bd_cuando_el_decisor_lo_indica(self, responder_desde_bd):
        responder_desde_bd.return_value = "Cursos registrados: 3."
        request = self.factory.post(reverse("agente_ajax"), data={"pregunta": "cuantos cursos hay"})
        _request_with_session(request, ROLE_EVALUADOR)

        response = agente_ajax(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["datos"]["source"], "bd")
        self.assertEqual(payload["datos"]["answer"], "Cursos registrados: 3.")


class RoleAjaxEndpointTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.usuario = SimpleNamespace(
            id_usuario=1,
            nombre="Ana",
            apellido_paterno="Perez",
            apellido_materno="Lopez",
            correo="ana@example.com",
            curp="PELA900101MDFRPN09",
            rol=SimpleNamespace(nombre_rol=ROLE_EVALUADOR),
            institucion=SimpleNamespace(nombre="Instituto"),
        )

    @patch("apps.users.api.roles.VistasBdService.contexto_docente")
    def test_datos_docente_ajax_responde_json(self, contexto_docente):
        contexto_docente.return_value = {
            "usuario": self.usuario,
            "total_cursos": 0,
            "total_procesos": 0,
            "cursos": [],
            "procesos": [],
        }
        request = self.factory.get("/docente/ajax/datos/")
        _request_with_session(request, ROLE_DOCENTE)

        response = datos_docente_ajax(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["estado"], "ok")
        self.assertEqual(payload["datos"]["total_cursos"], 0)

    @patch("apps.users.api.roles.VistasBdService.contexto_evaluador")
    def test_datos_evaluador_ajax_responde_json(self, contexto_evaluador):
        contexto_evaluador.return_value = {
            "usuario": self.usuario,
            "total_cursos": 2,
            "total_pendientes": 1,
            "total_aprobaciones": 1,
            "total_aprobaciones_evaluador": 1,
            "total_procesos": 3,
            "cursos_pendientes": [],
            "aprobaciones": [],
        }
        request = self.factory.get("/evaluador/ajax/datos/")
        _request_with_session(request, ROLE_EVALUADOR)

        response = datos_evaluador_ajax(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["datos"]["total_pendientes"], 1)

    @patch("apps.users.api.roles.VistasBdService.contexto_generador")
    def test_datos_generador_ajax_responde_json(self, contexto_generador):
        contexto_generador.return_value = {
            "usuario": self.usuario,
            "total_cursos": 4,
            "total_borradores": 1,
            "total_pendientes": 1,
            "total_aprobados": 2,
            "estadisticas_estados": [],
            "cursos": [],
            "aprobaciones": [],
        }
        request = self.factory.get("/generador/ajax/datos/")
        _request_with_session(request, ROLE_GENERADOR)

        response = datos_generador_ajax(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["datos"]["total_aprobados"], 2)
