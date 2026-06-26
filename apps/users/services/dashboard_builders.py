"""
Builders de contexto para dashboards por rol
"""
from django.db.models import Count, Q
from apps.users.models import Usuario, Curso, ProcesoEscalafon, ProcesoAprobacionCursos, BitacoraEvento
from apps.users.repositories import (
    UsuarioRepository, CursoRepository, ProcesoEscalafonRepository,
    ProcesoAprobacionRepository, BitacoraEventoRepository
)
from apps.users.serializers import (
    UsuarioSerializer, CursoSerializer, ProcesoEscalafonSerializer,
    ProcesoAprobacionSerializer, BitacoraEventoSerializer
)
from apps.users.models import proceso_aprobacion_cursos

class DashboardContextBuilder:
    """Constructor base de contexto para dashboards"""
    LIMITE_RECIENTES = 8
    
    @staticmethod
    def _base_context(request):
        """Construye contexto base común a todos los dashboards"""
        usuario = UsuarioRepository.get_by_id(request.session.get("usuario_id")) if request.session.get("usuario_id") else None
        
        return {
            "usuario": usuario,
            "usuario_nombre": request.session.get("usuario_nombre"),
            "usuario_rol": request.session.get("usuario_rol"),
            "perfil_usuario": UsuarioSerializer.to_dict(usuario) if usuario else {},
        }
    
    @staticmethod
    def datos_no_modelados():
        """Retorna lista de datos que aún no están modelados"""
        return {
            "preguntas": "No existe modelo para banco de preguntas, reactivos, opciones, respuestas correctas ni taxonomia Bloom.",
            "evaluaciones_formales": "No existe modelo separado de evaluaciones/examenes; se esta usando Curso como fuente disponible.",
            "calendario": "No existe modelo para eventos, fecha_inicio, fecha_fin, sede, hora o responsable.",
            "reportes": "No existen modelos para resultados, puntajes, intentos, dificultad, confiabilidad o tasa de aprobacion por sustentante.",
            "perfil_institucional": "Institucion solo expone nombre, tipo y activo; no hay clave, direccion, telefono o cedulas profesionales.",
            "estadisticas_generador": "No hay modelos de inscripciones, avance, abandono, calidad promedio, alcance o recomendaciones IA persistidas.",
        }


class EvaluadorContextBuilder(DashboardContextBuilder):
    """Constructor de contexto para dashboard de evaluador"""
    
    @staticmethod
    def build(request):
        """Construye contexto completo para evaluador"""
        context = DashboardContextBuilder._base_context(request)
        usuario_id = context["usuario"].id_usuario if context["usuario"] else None
        
        # Obtener datos usando repositories
        cursos = CursoRepository.get_recientes(DashboardContextBuilder.LIMITE_RECIENTES)
        cursos_pendientes = CursoRepository.get_pendientes_revision(DashboardContextBuilder.LIMITE_RECIENTES)
        if usuario_id:
            aprobaciones_usuario = ProcesoAprobacionCursos.objects.filter(
                evaluador_id=usuario_id
            )[:DashboardContextBuilder.LIMITE_RECIENTES]
        else:
            aprobaciones_usuario = []

        procesos_recientes = ProcesoEscalafonRepository.get_recientes(DashboardContextBuilder.LIMITE_RECIENTES)
        
        # Calcular métricas
        all_aprobaciones = ProcesoAprobacionCursos.objects.all()
        all_cursos = CursoRepository.get_all()
        
        context.update({
            # Datos crudos
            "cursos": cursos,
            "cursos_pendientes": cursos_pendientes,
            "aprobaciones": aprobaciones_usuario,
            "total_cursos": CursoRepository.model.objects.count(),
            "total_pendientes": CursoRepository.model.objects.filter(
                Q(estado__icontains="pendiente")
                | Q(estado__icontains="revision")
                | Q(estado__icontains="revisión")
            ).count(),
            "total_aprobaciones": all_aprobaciones.count(),
            "total_aprobaciones_evaluador": len(aprobaciones_usuario),
            "total_procesos": ProcesoEscalafonRepository.model.objects.count(),
            "ultimos_procesos": procesos_recientes,
            
            # Datos serializados
            "evaluaciones_bd": CursoSerializer.to_list(cursos),
            "validaciones_bd": CursoSerializer.to_list(cursos_pendientes),
            "calendario_procesos_bd": ProcesoEscalafonSerializer.to_list(procesos_recientes),
            
            # Métricas
            "metricas_evaluador": EvaluadorContextBuilder._metricas(
                all_cursos, cursos_pendientes, all_aprobaciones, aprobaciones_usuario
            ),
            
            # Reportes
            "reportes_bd": EvaluadorContextBuilder._reportes(all_cursos, all_aprobaciones),
            "datos_no_modelados": DashboardContextBuilder.datos_no_modelados(),
        })
        
        return context
    
    @staticmethod
    def _metricas(cursos, cursos_pendientes, aprobaciones, aprobaciones_usuario):
        """Calcula métricas para evaluador"""
        aprobadas = aprobaciones.filter(decision__icontains="aprob").count()
        rechazadas = aprobaciones.filter(
            Q(decision__icontains="rechaz")
            | Q(decision__icontains="no aprob")
        ).count()
        
        return {
            "evaluaciones_pendientes": cursos_pendientes.count(),
            "preguntas_pendientes_validar": 0,
            "preguntas_banco": 0,
            "evaluaciones_programadas": 0,
            "total_evaluaciones": cursos.count(),
            "evaluaciones_borrador": cursos.filter(estado__icontains="borrador").count(),
            "evaluaciones_publicadas": cursos.filter(estado__icontains="public").count(),
            "evaluaciones_aprobadas": aprobadas,
            "evaluaciones_rechazadas": rechazadas,
            "evaluaciones_revisadas_por_mi": len(aprobaciones_usuario),
        }
    
    @staticmethod
    def _reportes(cursos, aprobaciones):
        """Genera reportes para evaluador"""
        total_aprobaciones = aprobaciones.count()
        aprobadas = aprobaciones.filter(decision__icontains="aprob").count()
        tasa_aprobacion = round((aprobadas / total_aprobaciones) * 100, 2) if total_aprobaciones else 0
        
        return {
            "total_cursos": cursos.count(),
            "total_revisiones": total_aprobaciones,
            "tasa_aprobacion": tasa_aprobacion,
            "distribucion_cursos": list(
                cursos.values("estado").annotate(total=Count("id_curso")).order_by("estado")
            ),
            "distribucion_decisiones": list(
                aprobaciones.values("decision").annotate(total=Count("id_proceso")).order_by("decision")
            ),
        }


class GeneradorContextBuilder(DashboardContextBuilder):
    """Constructor de contexto para dashboard de generador de cursos"""
    
    @staticmethod
    def build(request):
        """Construye contexto completo para generador"""
        context = DashboardContextBuilder._base_context(request)
        usuario_id = context["usuario"].id_usuario if context["usuario"] else request.session.get("usuario_id")
        
        # Obtener datos del usuario
        cursos_usuario = CursoRepository.get_by_docente(usuario_id)
        cursos_recientes = cursos_usuario[:DashboardContextBuilder.LIMITE_RECIENTES]
        
        # Estadísticas
        total_cursos = cursos_usuario.count()
        total_borradores = cursos_usuario.filter(estado__icontains="borrador").count()
        total_pendientes = cursos_usuario.filter(
            Q(estado__icontains="pendiente")
            | Q(estado__icontains="revision")
            | Q(estado__icontains="revisión")
        ).count()
        total_aprobados = cursos_usuario.filter(estado__icontains="aprob").count()
        
        estados = list(
            cursos_usuario.values("estado")
            .annotate(total=Count("id_curso"))
            .order_by("estado")
        )
        
        aprobaciones = ProcesoAprobacionRepository.get_by_docente(
            usuario_id, DashboardContextBuilder.LIMITE_RECIENTES
        )
        
        context.update({
            # Datos crudos
            "cursos": cursos_recientes,
            "cursos_recientes": cursos_recientes,
            "estadisticas_estados": estados,
            "total_cursos": total_cursos,
            "total_borradores": total_borradores,
            "total_pendientes": total_pendientes,
            "total_aprobados": total_aprobados,
            "aprobaciones": aprobaciones,
            
            # Datos serializados
            "catalogo_cursos_bd": CursoSerializer.to_list(cursos_recientes),
            
            # Métricas
            "metricas_generador": {
                "cursos_activos": total_cursos,
                "validados": total_aprobados,
                "observaciones": cursos_usuario.filter(estado__icontains="observ").count(),
                "borradores": total_borradores,
                "pendientes": total_pendientes,
            },
            
            # Estadísticas
            "estadisticas_cursos_bd": {
                "por_estado": estados,
                "total_cursos": total_cursos,
                "total_aprobados": total_aprobados,
                "total_pendientes": total_pendientes,
                "total_borradores": total_borradores,
            },
            
            "datos_no_modelados": DashboardContextBuilder.datos_no_modelados(),
        })
        
        return context


class DocenteContextBuilder(DashboardContextBuilder):
    """Constructor de contexto para dashboard de docente"""
    
    @staticmethod
    def build(request):
        """Construye contexto completo para docente"""
        context = DashboardContextBuilder._base_context(request)
        usuario_id = request.session.get("usuario_id")
        
        # Obtener datos
        cursos = CursoRepository.get_by_docente(usuario_id, DashboardContextBuilder.LIMITE_RECIENTES)
        procesos = ProcesoEscalafonRepository.get_by_usuario(usuario_id, DashboardContextBuilder.LIMITE_RECIENTES)
        
        context.update({
            "cursos": cursos,
            "procesos": procesos,
            "total_cursos": CursoRepository.get_by_docente(usuario_id).count(),
            "total_procesos": ProcesoEscalafonRepository.get_by_usuario(usuario_id).count(),
            "proceso_actual": procesos.first() if procesos else None,
        })
        
        return context


class AdminContextBuilder(DashboardContextBuilder):
    """Constructor de contexto para dashboard de administrador"""
    
    @staticmethod
    def build(request):
        """Construye contexto completo para admin"""
        context = DashboardContextBuilder._base_context(request)
        
        # Obtener datos
        eventos_recientes = BitacoraEventoRepository.get_recientes(DashboardContextBuilder.LIMITE_RECIENTES)
        
        context.update({
            "total_usuarios": UsuarioRepository.model.objects.count(),
            "total_activos": UsuarioRepository.count_activos(),
            "eventos_recientes": eventos_recientes,
            "eventos_recientes_bd": BitacoraEventoSerializer.to_list(eventos_recientes),
        })
        
        return context


# Mantener compatibilidad hacia atrás
class VistasBdService:
    """Servicio legado - mantiene compatibilidad con código existente"""
    LIMITE_RECIENTES = DashboardContextBuilder.LIMITE_RECIENTES
    
    @staticmethod
    def contexto_evaluador(request):
        return EvaluadorContextBuilder.build(request)
    
    @staticmethod
    def contexto_generador(request):
        return GeneradorContextBuilder.build(request)
    
    @staticmethod
    def contexto_docente(request):
        return DocenteContextBuilder.build(request)
    
    @staticmethod
    def contexto_admin(request):
        return AdminContextBuilder.build(request)
    
    @staticmethod
    def datos_no_modelados():
        return DashboardContextBuilder.datos_no_modelados()
