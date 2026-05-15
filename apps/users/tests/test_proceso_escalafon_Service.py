from django.test import TestCase
from apps.users.models import ProcesoEscalafon, Usuario
from apps.users.services import proceso_escalafon_service


class ProcesoEscalafonServiceTest(TestCase):

    def setUp(self):
        # Crear usuario de prueba
        self.usuario = Usuario.objects.create(
            username="testuser",
            password="12345"
        )

        # Crear proceso de prueba
        self.proceso = ProcesoEscalafon.objects.create(
            usuario_id=self.usuario.id,
            folio="FOLIO123",
            tipo_proceso="tipo1",
            ciclo_escolar="2024",
            estado_id=1,
            funcion="funcion",
            tipo_sostenimiento="publico",
            tipo_valoracion="valoracion",
            datos_multifactores="datos",
            estatus="pendiente"
        )

    # 🔹 Test obtener procesos por usuario
    def test_obtener_procesos_usuario(self):
        procesos = proceso_escalafon_service.obtener_procesos_usuario(self.usuario.id)
        self.assertEqual(procesos.count(), 1)

    # 🔹 Test obtener por folio
    def test_obtener_proceso_por_folio(self):
        proceso = proceso_escalafon_service.obtener_proceso_por_folio("FOLIO123")
        self.assertEqual(proceso.folio, "FOLIO123")

    # 🔹 Test crear proceso
    def test_crear_proceso(self):
        proceso = proceso_escalafon_service.crear_proceso(
            usuario_id=self.usuario.id,
            folio="FOLIO456",
            tipo_proceso="tipo2",
            ciclo_escolar="2025",
            estado_id=2,
            funcion="otra",
            tipo_sostenimiento="privado",
            tipo_valoracion="otra",
            datos_multifactores="datos2",
            estatus="activo"
        )

        self.assertIsNotNone(proceso)
        self.assertEqual(proceso.folio, "FOLIO456")

    # 🔹 Test actualizar estado
    def test_actualizar_estado_proceso(self):
        proceso = proceso_escalafon_service.actualizar_estado_proceso("FOLIO123", "aprobado")
        self.assertEqual(proceso.estatus, "aprobado")

    # 🔹 Test filtrar por estado
    def test_obtener_procesos_por_estado(self):
        procesos = proceso_escalafon_service.obtener_procesos_por_estado(1)
        self.assertEqual(procesos.count(), 1)

    # 🔹 Test filtrar por ciclo escolar
    def test_obtener_procesos_ciclo_escolar(self):
        procesos = proceso_escalafon_service.obtener_procesos_ciclo_escolar("2024")
        self.assertEqual(procesos.count(), 1)