"""
Serializadores para convertir modelos a diccionarios/JSON
"""


class UsuarioSerializer:
    """Serializa Usuario a dict"""
    
    @staticmethod
    def to_dict(usuario):
        if not usuario:
            return None
        
        return {
            "id": usuario.id_usuario,
            "nombre_completo": f"{usuario.nombre} {usuario.apellido_paterno} {usuario.apellido_materno or ''}".strip(),
            "nombre": usuario.nombre,
            "apellido_paterno": usuario.apellido_paterno,
            "apellido_materno": usuario.apellido_materno or "",
            "correo": usuario.correo,
            "curp": usuario.curp,
            "rol": getattr(usuario.rol, "nombre_rol", ""),
            "institucion": getattr(usuario.institucion, "nombre", ""),
            "activo": usuario.activo,
            "fecha_registro": usuario.fecha_registro,
            "ultimo_acceso": usuario.ultimo_acceso,
        }
    
    @staticmethod
    def to_list(usuarios):
        return [UsuarioSerializer.to_dict(u) for u in usuarios]
    
    @staticmethod
    def simple(usuario):
        """Serialización simple solo con datos esenciales"""
        if not usuario:
            return None
        return {
            "id": usuario.id_usuario,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
        }


class CursoSerializer:
    """Serializa Curso a dict"""
    
    @staticmethod
    def to_dict(curso):
        if not curso:
            return None
        
        return {
            "id": curso.id_curso,
            "titulo": curso.titulo,
            "descripcion": curso.descripcion or "",
            "estado": curso.estado or "Sin estado",
            "generado_con_ia": curso.generado_con_ia,
            "version": curso.version,
            "fecha_creacion": curso.fecha_creacion,
            "fecha_aprobacion": curso.fecha_aprobacion,
            "docente": getattr(curso.docente, "nombre", ""),
            "docente_id": getattr(curso.docente, "id_usuario", None),
            "contenido_json": curso.contenido_json or {},
        }
    
    @staticmethod
    def to_list(cursos):
        return [CursoSerializer.to_dict(c) for c in cursos]
    
    @staticmethod
    def simple(curso):
        """Serialización simple"""
        if not curso:
            return None
        return {
            "id": curso.id_curso,
            "titulo": curso.titulo,
            "estado": curso.estado,
        }


class ProcesoEscalafonSerializer:
    """Serializa ProcesoEscalafon a dict"""
    
    @staticmethod
    def to_dict(proceso):
        if not proceso:
            return None
        
        return {
            "folio": proceso.folio,
            "tipo_proceso": proceso.tipo_proceso,
            "ciclo_escolar": proceso.ciclo_escolar,
            "estado": getattr(proceso.estado, "nombre", ""),
            "estatus": proceso.estatus,
            "funcion": proceso.funcion,
            "tipo_sostenimiento": proceso.tipo_sostenimiento,
            "tipo_valoracion": proceso.tipo_valoracion,
            "fecha_registro": proceso.fecha_registro,
            "usuario": getattr(proceso.usuario, "nombre", ""),
            "usuario_id": getattr(proceso.usuario, "id_usuario", None),
        }
    
    @staticmethod
    def to_list(procesos):
        return [ProcesoEscalafonSerializer.to_dict(p) for p in procesos]


class ProcesoAprobacionSerializer:
    """Serializa ProcesoAprobacionCursos a dict"""
    
    @staticmethod
    def to_dict(aprobacion):
        if not aprobacion:
            return None
        
        return {
            "id": aprobacion.id_proceso,
            "curso": getattr(aprobacion.curso, "titulo", ""),
            "curso_id": getattr(aprobacion.curso, "id_curso", None),
            "evaluador": getattr(aprobacion.evaluador, "nombre", ""),
            "evaluador_id": getattr(aprobacion.evaluador, "id_usuario", None),
            "decision": aprobacion.decision or "",
            "comentarios": aprobacion.comentarios or "",
            "fecha_revision": aprobacion.fecha_revision,
        }
    
    @staticmethod
    def to_list(aprobaciones):
        return [ProcesoAprobacionSerializer.to_dict(a) for a in aprobaciones]


class BitacoraEventoSerializer:
    """Serializa BitacoraEvento a dict"""
    
    @staticmethod
    def to_dict(evento):
        if not evento:
            return None
        
        return {
            "id": evento.id_evento,
            "usuario": getattr(evento.usuario, "nombre", ""),
            "usuario_id": getattr(evento.usuario, "id_usuario", None),
            "tipo_evento": evento.tipo_evento,
            "descripcion": evento.descripcion or "",
            "fecha_evento": evento.fecha_evento,
            "detalles": evento.detalles or "",
        }
    
    @staticmethod
    def to_list(eventos):
        return [BitacoraEventoSerializer.to_dict(e) for e in eventos]
