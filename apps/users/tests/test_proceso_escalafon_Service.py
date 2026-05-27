from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.users.services.proceso_escalafon_service import ProcesoEscalafonService


class ProcesoEscalafonServiceTest(SimpleTestCase):
    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_obtener_procesos_usuario(self, proceso_model):
        queryset = MagicMock()
        proceso_model.objects.filter.return_value.order_by.return_value = queryset

        procesos = ProcesoEscalafonService.obtener_procesos_usuario(10)

        proceso_model.objects.filter.assert_called_once_with(usuario_id=10)
        self.assertEqual(procesos, queryset)

    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_obtener_proceso_por_folio(self, proceso_model):
        proceso = SimpleNamespace(folio="FOLIO123")
        proceso_model.objects.get.return_value = proceso

        resultado = ProcesoEscalafonService.obtener_proceso_por_folio("FOLIO123")

        proceso_model.objects.get.assert_called_once_with(folio="FOLIO123")
        self.assertEqual(resultado.folio, "FOLIO123")

    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_crear_proceso(self, proceso_model):
        proceso = MagicMock()
        proceso_model.return_value = proceso

        resultado = ProcesoEscalafonService.crear_proceso(
            usuario_id=1,
            folio="FOLIO456",
            tipo_proceso="tipo2",
            ciclo_escolar="2025",
            estado_id=2,
            funcion="otra",
            tipo_sostenimiento="privado",
            tipo_valoracion="otra",
            datos_multifactores={"puntaje": 90},
            estatus="activo",
        )

        proceso_model.assert_called_once_with(
            usuario_id=1,
            folio="FOLIO456",
            tipo_proceso="tipo2",
            ciclo_escolar="2025",
            estado_id=2,
            funcion="otra",
            tipo_sostenimiento="privado",
            tipo_valoracion="otra",
            datos_multifactores={"puntaje": 90},
            estatus="activo",
        )
        proceso.save.assert_called_once()
        self.assertEqual(resultado, proceso)

    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_actualizar_estado_proceso(self, proceso_model):
        proceso = MagicMock(estatus="pendiente")
        proceso_model.objects.get.return_value = proceso

        resultado = ProcesoEscalafonService.actualizar_estado_proceso("FOLIO123", "aprobado")

        proceso_model.objects.get.assert_called_once_with(folio="FOLIO123")
        self.assertEqual(resultado.estatus, "aprobado")
        proceso.save.assert_called_once()

    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_obtener_procesos_por_estado(self, proceso_model):
        queryset = MagicMock()
        proceso_model.objects.filter.return_value.order_by.return_value = queryset

        procesos = ProcesoEscalafonService.obtener_procesos_por_estado(1)

        proceso_model.objects.filter.assert_called_once_with(estado_id=1)
        self.assertEqual(procesos, queryset)

    @patch("apps.users.services.proceso_escalafon_service.ProcesoEscalafon")
    def test_obtener_procesos_ciclo_escolar(self, proceso_model):
        queryset = MagicMock()
        proceso_model.objects.filter.return_value.order_by.return_value = queryset

        procesos = ProcesoEscalafonService.obtener_procesos_ciclo_escolar("2024")

        proceso_model.objects.filter.assert_called_once_with(ciclo_escolar="2024")
        self.assertEqual(procesos, queryset)
