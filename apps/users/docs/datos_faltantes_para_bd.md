# Datos de las vistas que aun no existen en los modelos

Este archivo lista los datos que aparecen en las pantallas de Evaluador y Generador, pero que no tienen un campo o modelo claro en `apps/users/models`. No se modificaron modelos.

## Evaluador

### Banco de preguntas y validaciones
- Banco de preguntas/reactivos.
- ID publico de pregunta, por ejemplo `PV-2024-001`.
- Enunciado de la pregunta.
- Opciones A/B/C/D.
- Respuesta correcta.
- Justificacion generada por IA.
- Asignatura.
- Nivel educativo.
- Dimension.
- Taxonomia Bloom.
- Origen de pregunta: IA/manual.
- Estado de pregunta: pendiente, aprobada, rechazada, en revision.
- Comentarios de validacion por pregunta.
- Fecha de aprobacion/rechazo por pregunta.

Modelos actuales relacionados: ninguno especifico. `RetroalimentacionIaCurso` guarda sugerencias de IA, pero no esta enlazado a `Curso` ni representa preguntas.

### Evaluaciones
- Evaluacion como entidad separada de `Curso`.
- Tipo de evaluacion: horizontal, vertical, diagnostica, etc.
- Nivel educativo.
- Materia/asignatura.
- Numero de preguntas.
- Fecha de publicacion.
- Fecha de vigencia.
- Fecha programada.
- Duracion en minutos.
- Progreso de creacion.
- Revisores asignados y cantidad requerida.

Modelo actual relacionado: `Curso`, usado como fuente disponible para titulo, descripcion, estado, creador y fechas basicas. No cubre los campos anteriores.

### Calendario
- Evento de calendario.
- Fecha inicio y fecha fin.
- Hora inicio y hora fin.
- Tipo de evento.
- Lugar/sede.
- Color/categoria visual.
- Tiempo restante calculado por evento.
- Responsable del evento.

Modelo actual relacionado: `ProcesoEscalafon` tiene `fecha_registro`, `tipo_proceso`, `ciclo_escolar` y `estatus`, pero no fecha fin, hora, sede ni evento calendario.

### Reportes estadisticos
- Confiabilidad alpha.
- Dificultad media.
- Tasa de aprobacion por sustentante/evaluacion.
- Distribucion de puntajes.
- Resultados por dimension.
- Tendencias temporales.
- Exportaciones PDF/Excel registradas.
- Entidad federativa de reporte.
- Grupo/comparativo.

Modelos actuales relacionados: `ProcesoAprobacionCursos` permite contar decisiones sobre cursos, pero no resultados, puntajes ni intentos.

### Perfil evaluador
- Clave de institucion.
- Direccion de institucion.
- Telefono.
- Cedulas/titulos/certificaciones.

Modelo actual relacionado: `Usuario` contiene nombre, apellidos, correo, CURP y fecha de registro. `Institucion` contiene nombre, tipo y activo.

## Generador de cursos

### Dashboard y catalogo
- Proceso USICAMM asociado al curso como texto de convocatoria.
- Estado USICAMM separado del campo `Curso.estado`.
- Observaciones detalladas por dictaminacion.
- Curso bloqueado/desbloqueado para edicion.
- Nivel/categoria educativa del curso.
- Imagen o banner del curso.

Modelo actual relacionado: `Curso` contiene titulo, descripcion, estado, generado_con_ia, version y fechas basicas.

### Generador de cursos
- Modulos del curso.
- Lecciones por modulo.
- Recursos visuales.
- Criterios de acreditacion.
- Fechas del curso.
- Prompt usado para generar.
- Versiones de contenido generadas por IA.
- Estado de subida a USICAMM.

Modelo actual relacionado: `Curso` no guarda estructura modular ni recursos.

### Estadisticas de cursos
- Alcance en usuarios.
- Efectividad academica.
- Calidad promedio.
- Interes por categoria educativa.
- Tendencia de acreditacion semanal.
- Recomendaciones IA persistidas.
- Tasas de abandono.
- Incidencias tecnicas.

Modelos actuales relacionados: no hay modelos de inscripciones, progreso, resultados, calificaciones ni recomendaciones enlazadas a cursos.

### Perfil generador
- Telefono.
- Cedulas y titulos verificados.
- Registro profesional.
- Cursos publicados como metricas historicas independientes.
- Diplomados creados.
- Impacto docente.

Modelos actuales relacionados: `Usuario`, `Institucion` y conteos derivados de `Curso`.

## Datos que ya se estan usando desde BD en las vistas

- Usuario en sesion: nombre, apellidos, correo, CURP, rol, institucion, fecha de registro.
- Cursos: titulo, descripcion, estado, generado con IA, version, fecha de creacion, fecha de aprobacion y creador.
- Procesos de escalafon: folio, tipo, ciclo escolar, estado, estatus, funcion, sostenimiento, valoracion y fecha de registro.
- Aprobaciones de cursos: curso, evaluador, iteracion, decision, comentarios y fecha de revision.
- Bitacora de eventos: usuario, tipo de evento, descripcion, fecha, IP y detalles.
