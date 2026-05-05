from apps.users.models import Curso

class CursoService:

    @staticmethod
    def obtener_cursos_docente(usuario_id):
        return Curso.objects.filter(
            docente_id=usuario_id
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_cursos_institucion(institucion_id):
        return Curso.objects.none()

    @staticmethod
    def obtener_cursos_ciclo_escolar(ciclo_escolar):
        return Curso.objects.none()

    @staticmethod
    def obtener_curso_por_id(curso_id):
        return Curso.objects.get(id_curso=curso_id)

    @staticmethod
    def crear_curso(titulo, descripcion, docente_id, estado='Borrador', generado_con_ia=False):
        return Curso.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            docente_id=docente_id,
            estado=estado,
            generado_con_ia=generado_con_ia,
            version=1,
        )

    @staticmethod
    def actualizar_curso(curso_id, titulo=None, descripcion=None, estado=None):
        curso = CursoService.obtener_curso_por_id(curso_id)
        
        if titulo is not None:
            curso.titulo = titulo
        if descripcion is not None:
            curso.descripcion = descripcion
        if estado is not None:
            curso.estado = estado
        
        curso.save()
        return curso

    @staticmethod
    def desactivar_curso(curso_id):
        curso = CursoService.obtener_curso_por_id(curso_id)
        curso.estado = 'Inactivo'
        curso.save(update_fields=["estado"])
        return curso

    @staticmethod
    def obtener_total_cursos_activos():
        return Curso.objects.all().count()