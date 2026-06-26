"""
Capa de repositorio para acceso a datos (abstracción del ORM)
"""
from django.db.models import Count, Q
from apps.users.models import Usuario, Curso, ProcesoEscalafon, ProcesoAprobacionCursos, BitacoraEvento


class BaseRepository:
    """Clase base para todos los repositorios"""
    model = None
    
    @classmethod
    def get_by_id(cls, pk):
        """Obtiene un registro por ID"""
        return cls.model.objects.get(pk=pk)
    
    @classmethod
    def get_all(cls, limit=None):
        """Obtiene todos los registros"""
        queryset = cls.model.objects.all()
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def create(cls, **kwargs):
        """Crea un nuevo registro"""
        return cls.model.objects.create(**kwargs)
    
    @classmethod
    def update(cls, pk, **kwargs):
        """Actualiza un registro"""
        obj = cls.get_by_id(pk)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj
    
    @classmethod
    def delete(cls, pk):
        """Elimina un registro"""
        cls.get_by_id(pk).delete()


class UsuarioRepository(BaseRepository):
    """Repositorio para Usuario"""
    model = Usuario
    
    @classmethod
    def get_by_correo(cls, correo):
        """Obtiene usuario por correo"""
        return cls.model.objects.select_related("rol", "institucion").filter(
            correo=correo
        ).first()
    
    @classmethod
    def get_by_rol(cls, nombre_rol):
        """Obtiene usuarios por rol"""
        return cls.model.objects.select_related("rol", "institucion").filter(
            rol__nombre_rol=nombre_rol
        )
    
    @classmethod
    def get_activos(cls, limit=None):
        """Obtiene usuarios activos"""
        queryset = cls.model.objects.select_related("rol", "institucion").filter(
            activo=True
        )
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def count_activos(cls):
        """Cuenta usuarios activos"""
        return cls.model.objects.filter(activo=True).count()


class CursoRepository(BaseRepository):
    """Repositorio para Curso"""
    model = Curso
    
    @classmethod
    def get_by_docente(cls, docente_id, limit=None):
        """Obtiene cursos de un docente"""
        queryset = cls.model.objects.select_related("docente").filter(
            docente_id=docente_id
        ).order_by("-fecha_creacion")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_by_estado(cls, estado, limit=None):
        """Obtiene cursos por estado"""
        queryset = cls.model.objects.select_related("docente").filter(
            estado__icontains=estado
        ).order_by("-fecha_creacion")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_pendientes_revision(cls, limit=None):
        """Obtiene cursos pendientes de revisión"""
        queryset = cls.model.objects.select_related("docente").filter(
            Q(estado__icontains="pendiente")
            | Q(estado__icontains="revision")
            | Q(estado__icontains="revisión")
        ).order_by("-fecha_creacion")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_aprobados(cls, limit=None):
        """Obtiene cursos aprobados"""
        queryset = cls.model.objects.select_related("docente").filter(
            estado__icontains="aprob"
        ).order_by("-fecha_creacion")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def contar_por_estado(cls, docente_id=None):
        """Cuenta cursos agrupados por estado"""
        queryset = cls.model.objects.all()
        if docente_id:
            queryset = queryset.filter(docente_id=docente_id)
        return list(
            queryset.values("estado").annotate(total=Count("id_curso")).order_by("estado")
        )
    
    @classmethod
    def get_recientes(cls, limit=8):
        """Obtiene cursos recientes"""
        return cls.model.objects.select_related("docente").order_by(
            "-fecha_creacion"
        )[:limit]


class ProcesoEscalafonRepository(BaseRepository):
    """Repositorio para ProcesoEscalafon"""
    model = ProcesoEscalafon
    
    @classmethod
    def get_by_usuario(cls, usuario_id, limit=None):
        """Obtiene procesos de escalafón de un usuario"""
        queryset = cls.model.objects.select_related("usuario", "estado").filter(
            usuario_id=usuario_id
        ).order_by("-fecha_registro")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_recientes(cls, limit=8):
        """Obtiene procesos recientes"""
        return cls.model.objects.select_related("usuario", "estado").order_by(
            "-fecha_registro"
        )[:limit]


class ProcesoAprobacionRepository(BaseRepository):
    """Repositorio para ProcesoAprobacionCursos"""
    model = ProcesoAprobacionCursos
    
    @staticmethod
    def get_by_evaluador(evaluador_id, limit=None):
        qs = ProcesoAprobacionCursos.objects.filter(evaluador_id=evaluador_id)  # ✅ CORRECTO
        if limit:
            qs = qs[:limit]
        return qs
    
    @classmethod
    def get_by_curso(cls, curso_id):
        """Obtiene aprobaciones de un curso"""
        return cls.model.objects.select_related("evaluador").filter(
            curso_id=curso_id
        ).order_by("-fecha_revision")
    
    @classmethod
    def get_by_docente(cls, docente_id, limit=None):
        """Obtiene aprobaciones de cursos de un docente"""
        queryset = cls.model.objects.select_related("curso", "evaluador").filter(
            curso__docente_id=docente_id
        ).order_by("-fecha_revision")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_recientes(cls, limit=8):
        """Obtiene aprobaciones recientes"""
        return cls.model.objects.select_related("curso", "evaluador").order_by(
            "-fecha_revision"
        )[:limit]


class BitacoraEventoRepository(BaseRepository):
    """Repositorio para BitacoraEvento"""
    model = BitacoraEvento
    
    @classmethod
    def get_by_usuario(cls, usuario_id, limit=None):
        """Obtiene eventos de un usuario"""
        queryset = cls.model.objects.select_related("usuario").filter(
            usuario_id=usuario_id
        ).order_by("-fecha_evento")
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_recientes(cls, limit=8):
        """Obtiene eventos recientes"""
        return cls.model.objects.select_related("usuario").order_by(
            "-fecha_evento"
        )[:limit]
    
    @classmethod
    def registrar(cls, usuario_id, tipo_evento, descripcion, detalles=None):
        """Registra un evento en la bitácora"""
        return cls.create(
            usuario_id=usuario_id,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            detalles=detalles
        )
