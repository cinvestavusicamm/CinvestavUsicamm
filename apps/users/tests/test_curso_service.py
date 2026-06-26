from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.users.services.curso_service import CursoService


class CursoServiceTests(SimpleTestCase):
    @patch("apps.users.services.curso_service.Curso")
    def test_obtener_cursos_docente_filtra_por_docente(self, curso_model):
        queryset = MagicMock()
        curso_model.objects.filter.return_value.order_by.return_value = queryset

        cursos = CursoService.obtener_cursos_docente(12)

        curso_model.objects.filter.assert_called_once_with(docente_id=12)
        self.assertEqual(cursos, queryset)

    @patch("apps.users.services.curso_service.Curso")
    def test_crear_curso_guarda_datos_base(self, curso_model):
        curso = MagicMock()
        curso_model.objects.create.return_value = curso

        resultado = CursoService.crear_curso(
            titulo="Curso de prueba",
            descripcion="Descripcion",
            docente_id=12,
            generado_con_ia=True,
        )

        curso_model.objects.create.assert_called_once_with(
            titulo="Curso de prueba",
            descripcion="Descripcion",
            docente_id=12,
            estado="Borrador",
            generado_con_ia=True,
            version=1,
        )
        self.assertEqual(resultado, curso)

    @patch("apps.users.services.curso_service.CursoService.obtener_curso_por_id")
    def test_actualizar_curso_actualiza_solo_campos_recibidos(self, obtener_curso_por_id):
        curso = MagicMock(titulo="Anterior", descripcion="Vieja", estado="Borrador")
        obtener_curso_por_id.return_value = curso

        resultado = CursoService.actualizar_curso(3, titulo="Nuevo", estado="Publicado")

        self.assertEqual(resultado.titulo, "Nuevo")
        self.assertEqual(resultado.descripcion, "Vieja")
        self.assertEqual(resultado.estado, "Publicado")
        curso.save.assert_called_once()

    @patch("apps.users.services.curso_service.CursoService.obtener_curso_por_id")
    def test_desactivar_curso_marca_inactivo(self, obtener_curso_por_id):
        curso = MagicMock(estado="Publicado")
        obtener_curso_por_id.return_value = curso

        resultado = CursoService.desactivar_curso(3)

        self.assertEqual(resultado.estado, "Inactivo")
        curso.save.assert_called_once_with(update_fields=["estado"])
