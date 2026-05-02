from apps.users.models import Curso


class CursoService:

    @staticmethod
    def obtener_cursos_docente(usuario_id):
        return Curso.objects.filter(
            docente_id=usuario_id,
            activo=True
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_cursos_institucion(institucion_id):
        return Curso.objects.filter(
            institucion_id=institucion_id,
            activo=True
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_cursos_ciclo_escolar(ciclo_escolar):
        return Curso.objects.filter(
            ciclo_escolar=ciclo_escolar,
            activo=True
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_curso_por_id(curso_id):
        return Curso.objects.get(id_curso=curso_id)

    @staticmethod
    def crear_curso(nombre, descripcion, docente_id, institucion_id, ciclo_escolar):
        return Curso.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            docente_id=docente_id,
            institucion_id=institucion_id,
            ciclo_escolar=ciclo_escolar,
        )

    @staticmethod
    def actualizar_curso(curso_id, nombre=None, descripcion=None, ciclo_escolar=None):
        curso = CursoService.obtener_curso_por_id(curso_id)

        if nombre is not None:
            curso.nombre = nombre
        if descripcion is not None:
            curso.descripcion = descripcion
        if ciclo_escolar is not None:
            curso.ciclo_escolar = ciclo_escolar

        curso.save()
        return curso

    @staticmethod
    def desactivar_curso(curso_id):
        curso = CursoService.obtener_curso_por_id(curso_id)
        curso.activo = False
        curso.save(update_fields=["activo"])
        return curso

    @staticmethod
    def obtener_total_cursos_activos():
        return Curso.objects.filter(activo=True).count()
