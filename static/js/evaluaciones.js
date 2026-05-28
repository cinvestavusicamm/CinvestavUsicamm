// ==================== EVALUACIONES.JS ====================
// Módulo para gestionar evaluaciones con preguntas del banco

// Variables globales
let evaluacionesGlobales = [];
let preguntasDisponibles = [];
let evaluacionEditando = null;
let preguntasSeleccionadas = [];
let preguntasSeleccionadasEdicion = [];
let preguntasFiltradasActuales = [];
let preguntasFiltradasEdicion = [];

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', function() {
    cargarDatosIniciales();
    inicializarEventosEvaluaciones();
    renderizarEvaluaciones();
    inicializarModales();
});

function cargarDatosIniciales() {
    // Cargar preguntas del localStorage
    const storedPreguntas = localStorage.getItem('escalafonia_preguntas');
    if (storedPreguntas) {
        preguntasDisponibles = JSON.parse(storedPreguntas);
    } else {
        preguntasDisponibles = obtenerPreguntasEjemplo();
        localStorage.setItem('escalafonia_preguntas', JSON.stringify(preguntasDisponibles));
    }
    
    // Cargar evaluaciones del localStorage
    const storedEvaluaciones = localStorage.getItem('escalafonia_evaluaciones');
    if (storedEvaluaciones) {
        evaluacionesGlobales = JSON.parse(storedEvaluaciones);
    } else {
        evaluacionesGlobales = obtenerEvaluacionesEjemplo();
        guardarEvaluaciones();
    }
}

function obtenerPreguntasEjemplo() {
    return [
        {
            id: 1,
            enunciado: "¿Cuál de las siguientes estrategias es más efectiva para fomentar la lectura en primaria?",
            asignatura: "espanol",
            nivel: "primaria",
            dimension: "pedagogica",
            tipo: "opcion_multiple",
            estado: "validada",
            fecha: "15/06/2024",
            bloom: "aplicar",
            dificultad: "media",
            opciones: ["Lectura en voz alta diaria", "Talleres de escritura creativa", "Círculos de lectura con padres", "Uso exclusivo de libros digitales"],
            respuesta_correcta: "2",
            retroalimentacion: "Los círculos de lectura fomentan la participación activa y el gusto por la lectura."
        },
        {
            id: 2,
            enunciado: "Un docente observa que varios estudiantes tienen dificultades con fracciones. ¿Cuál sería la intervención más apropiada según el enfoque de la NEM?",
            asignatura: "matematicas",
            nivel: "secundaria",
            dimension: "didactica",
            tipo: "caso_practico",
            estado: "validada",
            fecha: "14/06/2024",
            bloom: "analizar",
            dificultad: "alta",
            opciones: ["Realizar una evaluación diagnóstica", "Implementar actividades con material concreto", "Trabajar en equipos colaborativos", "Utilizar recursos digitales interactivos"],
            respuesta_correcta: "1",
            retroalimentacion: "El uso de material concreto ayuda a comprender conceptos abstractos como las fracciones."
        },
        {
            id: 3,
            enunciado: "Verdadero o Falso: La gamificación mejora significativamente la motivación intrínseca en estudiantes de preescolar.",
            asignatura: "pedagogia",
            nivel: "preescolar",
            dimension: "tic",
            tipo: "verdadero_falso",
            estado: "validada",
            fecha: "13/06/2024",
            bloom: "recordar",
            dificultad: "baja",
            opciones: ["Verdadero", "Falso"],
            respuesta_correcta: "true",
            retroalimentacion: "La gamificación ha demostrado aumentar la motivación y el compromiso en educación inicial."
        }
    ];
}

function obtenerEvaluacionesEjemplo() {
    return [
        {
            id: 1,
            nombre: "Promoción Horizontal 2026 - Matemáticas Primaria",
            descripcion: "Evaluación para promoción horizontal de maestros de matemáticas en nivel primaria.",
            tipo: "horizontal",
            estado: "publicada",
            fechaCreacion: "15/06/2024",
            fechaModificacion: "15/06/2024",
            fechaPublicacion: "15/06/2024",
            fechaVigencia: "30/09/2024",
            creador: "María Pérez",
            nivel: "primaria",
            asignaturas: ["matematicas"],
            preguntas: [1, 2],
            duracion: 90,
            publicada: true,
            borrador: false
        },
        {
            id: 2,
            nombre: "Promoción Vertical - Directores Secundaria",
            descripcion: "Evaluación para ascenso a cargos directivos en secundaria.",
            tipo: "vertical",
            estado: "borrador",
            fechaCreacion: "10/06/2024",
            fechaModificacion: "14/06/2024",
            creador: "Juan Rodríguez",
            nivel: "secundaria",
            asignaturas: ["gestion"],
            preguntas: [],
            duracion: 120,
            publicada: false,
            borrador: true,
            progreso: 65
        }
    ];
}

function guardarEvaluaciones() {
    localStorage.setItem('escalafonia_evaluaciones', JSON.stringify(evaluacionesGlobales));
}

// ==================== RENDERIZADO DE EVALUACIONES ====================

function renderizarEvaluaciones() {
    const container = document.querySelector('.grid-evaluaciones');
    if (!container) return;
    
    const filtroTipo = document.getElementById('filtroTipoEvaluacion')?.value || 'todas';
    const filtroEstado = document.getElementById('filtroEstado')?.value || 'todas';
    const busqueda = document.getElementById('buscadorEvaluaciones')?.value.toLowerCase() || '';
    
    let evaluacionesFiltradas = evaluacionesGlobales.filter(eval => {
        if (filtroTipo !== 'todas' && eval.tipo !== filtroTipo) return false;
        if (filtroEstado !== 'todas') {
            if (filtroEstado === 'borrador' && !eval.borrador) return false;
            if (filtroEstado === 'publicada' && !eval.publicada) return false;
            if (filtroEstado === 'revision' && eval.estado !== 'revision') return false;
        }
        if (busqueda && !eval.nombre.toLowerCase().includes(busqueda) && !eval.descripcion.toLowerCase().includes(busqueda)) return false;
        return true;
    });
    
    if (evaluacionesFiltradas.length === 0) {
        container.innerHTML = `
            <div class="sin-resultados" style="grid-column: 1/-1; text-align: center; padding: 60px;">
                <i class="fas fa-folder-open" style="font-size: 64px; color: #cbd5e1; margin-bottom: 16px;"></i>
                <p style="color: #64748b;">No hay evaluaciones que coincidan con los filtros</p>
                <button class="btn btn-primary" id="btnCrearEvaluacionVacia">
                    <i class="fas fa-plus-circle"></i> Crear nueva evaluación
                </button>
            </div>
        `;
        const btnCrear = document.getElementById('btnCrearEvaluacionVacia');
        if (btnCrear) btnCrear.addEventListener('click', () => abrirModalCreacion());
        return;
    }
    
    container.innerHTML = evaluacionesFiltradas.map(eval => renderizarTarjetaEvaluacion(eval)).join('');
    
    // Agregar tarjeta de nueva evaluación
    const nuevaTarjeta = document.getElementById('btnNuevaEvaluacionCard');
    if (!nuevaTarjeta) {
        container.insertAdjacentHTML('beforeend', `
            <div class="tarjeta-nueva-evaluacion" id="btnNuevaEvaluacionCard">
                <div class="nueva-evaluacion-contenido">
                    <i class="fas fa-plus-circle"></i>
                    <h3>Crear Nueva Evaluación</h3>
                    <p>Diseña una nueva evaluación desde cero</p>
                </div>
            </div>
        `);
    }
    
    // Eventos de las tarjetas
    document.querySelectorAll('.btn-editar-evaluacion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            abrirModalEdicion(id);
        });
    });
    
    document.querySelectorAll('.btn-publicar-evaluacion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            publicarEvaluacion(id);
        });
    });
    
    document.querySelectorAll('.btn-programar-evaluacion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            programarEvaluacion(id);
        });
    });
    
    document.querySelectorAll('.btn-ver-evaluacion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            verEvaluacionDetalle(id);
        });
    });
    
    document.querySelectorAll('.btn-clonar-evaluacion').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            clonarEvaluacion(id);
        });
    });
    
    const btnNuevaCard = document.getElementById('btnNuevaEvaluacionCard');
    if (btnNuevaCard) btnNuevaCard.addEventListener('click', () => abrirModalCreacion());
    
    actualizarEstadisticasEvaluaciones();
    renderizarEvaluacionesRecientes();
}

function renderizarTarjetaEvaluacion(eval) {
    const estadoClass = eval.publicada ? 'publicada' : (eval.borrador ? 'borrador' : (eval.estado === 'revision' ? 'revision' : 'programada'));
    const estadoIcono = eval.publicada ? 'fa-check-circle' : (eval.borrador ? 'fa-edit' : (eval.estado === 'revision' ? 'fa-clipboard-check' : 'fa-calendar-check'));
    const estadoTexto = eval.publicada ? 'Publicada' : (eval.borrador ? 'Borrador' : (eval.estado === 'revision' ? 'En revisión' : 'Programada'));
    
    const nivelTexto = getNivelTexto(eval.nivel);
    const asignaturaTextos = eval.asignaturas.map(a => getAsignaturaTexto(a)).join(', ');
    const totalPreguntas = eval.preguntas.length;
    
    let fechaInfo = '';
    if (eval.publicada && eval.fechaVigencia) {
        fechaInfo = `
            <div class="evaluacion-fechas">
                <div class="fecha-item"><i class="fas fa-calendar-alt"></i><span><strong>Publicación:</strong> ${eval.fechaPublicacion}</span></div>
                <div class="fecha-item"><i class="fas fa-clock"></i><span><strong>Válida hasta:</strong> ${eval.fechaVigencia}</span></div>
            </div>
        `;
    } else if (eval.fechaProgramada) {
        fechaInfo = `
            <div class="evaluacion-fechas">
                <div class="fecha-item"><i class="fas fa-calendar-alt"></i><span><strong>Programada para:</strong> ${eval.fechaProgramada}</span></div>
                <div class="fecha-item"><i class="fas fa-user-clock"></i><span><strong>Duración:</strong> ${eval.duracion} minutos</span></div>
            </div>
        `;
    } else if (eval.borrador && eval.progreso !== undefined) {
        fechaInfo = `
            <div class="evaluacion-progreso">
                <div class="progreso-info"><span>Progreso:</span><span>${eval.progreso}%</span></div>
                <div class="progreso-bar"><div class="progreso-fill" style="width: ${eval.progreso}%"></div></div>
            </div>
        `;
    }
    
    let acciones = '';
    if (eval.borrador) {
        acciones = `
            <button class="btn btn-outline btn-sm btn-editar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-pen"></i> Continuar
            </button>
            <button class="btn btn-primary btn-sm btn-publicar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-check-circle"></i> Publicar
            </button>
        `;
    } else if (eval.publicada) {
        acciones = `
            <button class="btn btn-outline btn-sm btn-ver-evaluacion" data-id="${eval.id}">
                <i class="fas fa-eye"></i> Ver
            </button>
            <button class="btn btn-outline btn-sm btn-clonar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-copy"></i> Clonar
            </button>
        `;
    } else if (eval.estado === 'programada') {
        acciones = `
            <button class="btn btn-outline btn-sm btn-programar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-calendar"></i> Reprogramar
            </button>
            <button class="btn btn-primary btn-sm btn-publicar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-play-circle"></i> Activar
            </button>
        `;
    } else {
        acciones = `
            <button class="btn btn-outline btn-sm btn-ver-evaluacion" data-id="${eval.id}">
                <i class="fas fa-eye"></i> Ver
            </button>
            <button class="btn btn-outline btn-sm btn-clonar-evaluacion" data-id="${eval.id}">
                <i class="fas fa-copy"></i> Clonar
            </button>
        `;
    }
    
    return `
        <div class="tarjeta-evaluacion">
            <div class="evaluacion-header">
                <div class="evaluacion-estado evaluacion-${estadoClass}">
                    <i class="fas ${estadoIcono}"></i>
                    <span>${estadoTexto}</span>
                </div>
                <div class="evaluacion-acciones">
                    <button class="btn-icon btn-editar-evaluacion" data-id="${eval.id}" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
            <div class="evaluacion-contenido">
                <h3 class="evaluacion-titulo">${escapeHtml(eval.nombre)}</h3>
                <p class="evaluacion-descripcion">${escapeHtml(eval.descripcion)}</p>
                <div class="evaluacion-meta">
                    <div class="meta-item"><i class="fas fa-graduation-cap"></i><span>${nivelTexto}</span></div>
                    <div class="meta-item"><i class="fas fa-book"></i><span>${asignaturaTextos}</span></div>
                    <div class="meta-item"><i class="fas fa-question-circle"></i><span>${totalPreguntas} preguntas</span></div>
                </div>
                ${fechaInfo}
            </div>
            <div class="evaluacion-footer">
                ${acciones}
            </div>
        </div>
    `;
}

function renderizarEvaluacionesRecientes() {
    const container = document.querySelector('.tabla-recientes tbody');
    if (!container) return;
    
    const recientes = [...evaluacionesGlobales]
        .sort((a, b) => {
            const dateA = a.fechaModificacion.split('/').reverse().join('-');
            const dateB = b.fechaModificacion.split('/').reverse().join('-');
            return new Date(dateB) - new Date(dateA);
        })
        .slice(0, 5);
    
    if (recientes.length === 0) {
        container.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 40px;">No hay evaluaciones recientes</td></tr>`;
        return;
    }
    
    container.innerHTML = recientes.map(eval => {
        const tipoTexto = eval.tipo === 'horizontal' ? 'Horizontal' : (eval.tipo === 'vertical' ? 'Vertical' : 'Diagnóstica');
        const estadoClass = eval.publicada ? 'publicada' : (eval.borrador ? 'borrador' : (eval.estado === 'revision' ? 'revision' : 'programada'));
        const estadoTexto = eval.publicada ? 'Publicada' : (eval.borrador ? 'Borrador' : (eval.estado === 'revision' ? 'En revisión' : 'Programada'));
        
        return `
            <tr>
                <td>
                    <strong>${escapeHtml(eval.nombre)}</strong>
                    <small>${eval.tipo === 'horizontal' ? 'Promoción Horizontal' : (eval.tipo === 'vertical' ? 'Promoción Vertical' : 'Evaluación Diagnóstica')}</small>
                </td>
                <td>${tipoTexto}</td>
                <td>${eval.fechaModificacion}</td>
                <td><span class="badge badge-${estadoClass}">${estadoTexto}</span></td>
                <td>${escapeHtml(eval.creador)}</td>
                <td>
                    <button class="btn-icon btn-sm btn-editar-evaluacion" data-id="${eval.id}" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-ver-evaluacion" data-id="${eval.id}" title="Ver">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    document.querySelectorAll('.tabla-recientes .btn-editar-evaluacion').forEach(btn => {
        btn.addEventListener('click', () => abrirModalEdicion(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll('.tabla-recientes .btn-ver-evaluacion').forEach(btn => {
        btn.addEventListener('click', () => verEvaluacionDetalle(parseInt(btn.dataset.id)));
    });
}

function actualizarEstadisticasEvaluaciones() {
    const total = evaluacionesGlobales.length;
    const borradores = evaluacionesGlobales.filter(e => e.borrador).length;
    const publicadas = evaluacionesGlobales.filter(e => e.publicada).length;
    const programadas = evaluacionesGlobales.filter(e => e.estado === 'programada').length;
    
    const totalEl = document.querySelector('.estadistica-item:first-child .estadistica-contenido h3');
    const borradorEl = document.querySelector('.estadistica-item:nth-child(2) .estadistica-contenido h3');
    const publicadaEl = document.querySelector('.estadistica-item:nth-child(3) .estadistica-contenido h3');
    const programadaEl = document.querySelector('.estadistica-item:nth-child(4) .estadistica-contenido h3');
    
    if (totalEl) totalEl.textContent = total;
    if (borradorEl) borradorEl.textContent = borradores;
    if (publicadaEl) publicadaEl.textContent = publicadas;
    if (programadaEl) programadaEl.textContent = programadas;
}

// ==================== MODALES ====================

function inicializarModales() {
    // Crear modal de creación
    const modalCreacionHTML = `
        <div id="modalCreacionEvaluacion" class="modal-overlay">
            <div class="modal-eventos modal-eventos--lg">
                <div class="modal-header">
                    <h2><i class="fas fa-plus-circle"></i> Crear Nueva Evaluación</h2>
                    <button class="btn-cerrar-modal" id="cerrarModalCreacion"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div id="formCreacionEvaluacion">
                        <div class="form-grid">
                            <div class="grupo-formulario">
                                <label><i class="fas fa-tag"></i> Nombre de la evaluación *</label>
                                <input type="text" id="evalNombre" class="form-control" placeholder="Ej: Promoción Horizontal 2026">
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-chart-line"></i> Tipo de evaluación *</label>
                                <select id="evalTipo" class="form-control">
                                    <option value="horizontal">Promoción Horizontal</option>
                                    <option value="vertical">Promoción Vertical</option>
                                    <option value="diagnostica">Evaluación Diagnóstica</option>
                                </select>
                            </div>
                            <div class="grupo-formulario full-width">
                                <label><i class="fas fa-align-left"></i> Descripción</label>
                                <textarea id="evalDescripcion" rows="3" class="form-control"></textarea>
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-graduation-cap"></i> Nivel educativo *</label>
                                <select id="evalNivel" class="form-control">
                                    <option value="preescolar">Preescolar</option>
                                    <option value="primaria" selected>Primaria</option>
                                    <option value="secundaria">Secundaria</option>
                                    <option value="media_superior">Media Superior</option>
                                </select>
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-hourglass-half"></i> Duración (minutos)</label>
                                <input type="number" id="evalDuracion" class="form-control" value="90">
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-calendar-alt"></i> Fecha de publicación</label>
                                <input type="date" id="evalFechaPublicacion" class="form-control">
                            </div>
                        </div>
                        
                        <div class="selector-header">
                            <h4><i class="fas fa-clipboard-list"></i> Selecciona las preguntas</h4>
                            <div class="selector-acciones">
                                <button class="btn btn-sm btn-outline" id="seleccionarTodasPreguntas">Seleccionar todas</button>
                                <button class="btn btn-sm btn-outline" id="deseleccionarTodasPreguntas">Deseleccionar</button>
                            </div>
                        </div>
                        
                        <div class="panel-filtros">
                            <div class="filtros-header-collapsible" id="toggleFiltrosCreacion">
                                <h4><i class="fas fa-filter"></i> Filtros</h4>
                                <i class="fas fa-chevron-down"></i>
                            </div>
                            <div class="filtros-panel" id="filtrosCreacionPanel">
                                <div class="filtros-grid">
                                    <div class="filtro-grupo">
                                        <label>Nivel</label>
                                        <select id="filtroNivelCreacion" class="filtro-select">
                                            <option value="">Todos</option>
                                            <option value="preescolar">Preescolar</option>
                                            <option value="primaria">Primaria</option>
                                            <option value="secundaria">Secundaria</option>
                                            <option value="media_superior">Media Superior</option>
                                        </select>
                                    </div>
                                    <div class="filtro-grupo">
                                        <label>Asignatura</label>
                                        <select id="filtroAsignaturaCreacion" class="filtro-select">
                                            <option value="">Todas</option>
                                            <option value="espanol">Español</option>
                                            <option value="matematicas">Matemáticas</option>
                                            <option value="ciencias">Ciencias</option>
                                            <option value="historia">Historia</option>
                                            <option value="geografia">Geografía</option>
                                        </select>
                                    </div>
                                    <div class="filtro-grupo">
                                        <label>Dimensión</label>
                                        <select id="filtroDimensionCreacion" class="filtro-select">
                                            <option value="">Todas</option>
                                            <option value="pedagogica">Pedagógica</option>
                                            <option value="disciplinar">Disciplinar</option>
                                            <option value="didactica">Didáctica</option>
                                            <option value="gestion">Gestión</option>
                                            <option value="tic">TIC</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="filtros-acciones">
                                    <button class="btn btn-primary btn-sm" id="aplicarFiltrosCreacion">Filtrar</button>
                                    <button class="btn btn-outline btn-sm" id="limpiarFiltrosCreacion">Limpiar</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="contador-seleccion">
                            <i class="fas fa-check-circle"></i>
                            <span id="preguntasSeleccionadasCount">0</span> preguntas seleccionadas
                        </div>
                        
                        <div class="lista-preguntas" id="listaPreguntasCreacion"></div>
                        
                        <div class="grupo-botones">
                            <button class="btn btn-success" id="guardarEvaluacionBtn"><i class="fas fa-save"></i> Guardar Borrador</button>
                            <button class="btn btn-primary" id="guardarYPublicarBtn"><i class="fas fa-check-circle"></i> Publicar</button>
                            <button class="btn btn-secondary" id="cancelarCreacion">Cancelar</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal de edición
    const modalEdicionHTML = `
        <div id="modalEdicionEvaluacion" class="modal-overlay">
            <div class="modal-eventos modal-eventos--lg">
                <div class="modal-header">
                    <h2><i class="fas fa-edit"></i> Editar Evaluación</h2>
                    <button class="btn-cerrar-modal" id="cerrarModalEdicion"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div id="formEdicionEvaluacion">
                        <div class="form-grid">
                            <div class="grupo-formulario">
                                <label><i class="fas fa-tag"></i> Nombre de la evaluación *</label>
                                <input type="text" id="editEvalNombre" class="form-control">
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-chart-line"></i> Tipo de evaluación *</label>
                                <select id="editEvalTipo" class="form-control">
                                    <option value="horizontal">Promoción Horizontal</option>
                                    <option value="vertical">Promoción Vertical</option>
                                    <option value="diagnostica">Evaluación Diagnóstica</option>
                                </select>
                            </div>
                            <div class="grupo-formulario full-width">
                                <label><i class="fas fa-align-left"></i> Descripción</label>
                                <textarea id="editEvalDescripcion" rows="3" class="form-control"></textarea>
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-graduation-cap"></i> Nivel educativo *</label>
                                <select id="editEvalNivel" class="form-control">
                                    <option value="preescolar">Preescolar</option>
                                    <option value="primaria">Primaria</option>
                                    <option value="secundaria">Secundaria</option>
                                    <option value="media_superior">Media Superior</option>
                                </select>
                            </div>
                            <div class="grupo-formulario">
                                <label><i class="fas fa-hourglass-half"></i> Duración (minutos)</label>
                                <input type="number" id="editEvalDuracion" class="form-control">
                            </div>
                        </div>
                        
                        <div class="selector-header">
                            <h4><i class="fas fa-clipboard-list"></i> Selecciona las preguntas</h4>
                            <div class="selector-acciones">
                                <button class="btn btn-sm btn-outline" id="seleccionarTodasEdicion">Seleccionar todas</button>
                                <button class="btn btn-sm btn-outline" id="deseleccionarTodasEdicion">Deseleccionar</button>
                            </div>
                        </div>
                        
                        <div class="panel-filtros">
                            <div class="filtros-header-collapsible" id="toggleFiltrosEdicion">
                                <h4><i class="fas fa-filter"></i> Filtros</h4>
                                <i class="fas fa-chevron-down"></i>
                            </div>
                            <div class="filtros-panel" id="filtrosEdicionPanel">
                                <div class="filtros-grid">
                                    <div class="filtro-grupo">
                                        <label>Nivel</label>
                                        <select id="filtroNivelEdicion" class="filtro-select">
                                            <option value="">Todos</option>
                                            <option value="preescolar">Preescolar</option>
                                            <option value="primaria">Primaria</option>
                                            <option value="secundaria">Secundaria</option>
                                        </select>
                                    </div>
                                    <div class="filtro-grupo">
                                        <label>Asignatura</label>
                                        <select id="filtroAsignaturaEdicion" class="filtro-select">
                                            <option value="">Todas</option>
                                            <option value="espanol">Español</option>
                                            <option value="matematicas">Matemáticas</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="filtros-acciones">
                                    <button class="btn btn-primary btn-sm" id="aplicarFiltrosEdicion">Filtrar</button>
                                    <button class="btn btn-outline btn-sm" id="limpiarFiltrosEdicion">Limpiar</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="contador-seleccion">
                            <i class="fas fa-check-circle"></i>
                            <span id="preguntasSeleccionadasEdicionCount">0</span> preguntas seleccionadas
                        </div>
                        
                        <div class="lista-preguntas" id="listaPreguntasEdicion"></div>
                        
                        <div class="grupo-botones">
                            <button class="btn btn-success" id="actualizarEvaluacionBtn"><i class="fas fa-save"></i> Actualizar</button>
                            <button class="btn btn-secondary" id="cancelarEdicion">Cancelar</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalCreacionHTML);
    document.body.insertAdjacentHTML('beforeend', modalEdicionHTML);
    
    // Eventos modales
    document.getElementById('cerrarModalCreacion')?.addEventListener('click', cerrarModalCreacion);
    document.getElementById('cancelarCreacion')?.addEventListener('click', cerrarModalCreacion);
    document.getElementById('cerrarModalEdicion')?.addEventListener('click', cerrarModalEdicion);
    document.getElementById('cancelarEdicion')?.addEventListener('click', cerrarModalEdicion);
    
    document.getElementById('guardarEvaluacionBtn')?.addEventListener('click', () => guardarEvaluacion(false));
    document.getElementById('guardarYPublicarBtn')?.addEventListener('click', () => guardarEvaluacion(true));
    document.getElementById('actualizarEvaluacionBtn')?.addEventListener('click', actualizarEvaluacion);
    
    // Filtros
    document.getElementById('toggleFiltrosCreacion')?.addEventListener('click', function() {
        document.getElementById('filtrosCreacionPanel')?.classList.toggle('collapsed');
        this.classList.toggle('collapsed');
    });
    document.getElementById('toggleFiltrosEdicion')?.addEventListener('click', function() {
        document.getElementById('filtrosEdicionPanel')?.classList.toggle('collapsed');
        this.classList.toggle('collapsed');
    });
    
    document.getElementById('aplicarFiltrosCreacion')?.addEventListener('click', () => filtrarPreguntasCreacion());
    document.getElementById('limpiarFiltrosCreacion')?.addEventListener('click', () => limpiarFiltrosCreacion());
    document.getElementById('aplicarFiltrosEdicion')?.addEventListener('click', () => filtrarPreguntasEdicion());
    document.getElementById('limpiarFiltrosEdicion')?.addEventListener('click', () => limpiarFiltrosEdicion());
    
    document.getElementById('seleccionarTodasPreguntas')?.addEventListener('click', () => seleccionarTodasCreacion());
    document.getElementById('deseleccionarTodasPreguntas')?.addEventListener('click', () => deseleccionarTodasCreacion());
    document.getElementById('seleccionarTodasEdicion')?.addEventListener('click', () => seleccionarTodasEdicion());
    document.getElementById('deseleccionarTodasEdicion')?.addEventListener('click', () => deseleccionarTodasEdicion());
}

function abrirModalCreacion() {
    const modal = document.getElementById('modalCreacionEvaluacion');
    if (!modal) return;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Resetear formulario
    document.getElementById('evalNombre').value = '';
    document.getElementById('evalDescripcion').value = '';
    document.getElementById('evalTipo').value = 'horizontal';
    document.getElementById('evalNivel').value = 'primaria';
    document.getElementById('evalDuracion').value = '90';
    document.getElementById('evalFechaPublicacion').value = '';
    
    preguntasSeleccionadas = [];
    actualizarContadorSeleccion();
    cargarListaPreguntasCreacion();
}

function cerrarModalCreacion() {
    const modal = document.getElementById('modalCreacionEvaluacion');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function abrirModalEdicion(id) {
    const evaluacion = evaluacionesGlobales.find(e => e.id === id);
    if (!evaluacion) return;
    
    if (evaluacion.publicada) {
        mostrarNotificacion('No se puede editar una evaluación ya publicada', 'error');
        return;
    }
    
    evaluacionEditando = evaluacion;
    preguntasSeleccionadasEdicion = [...evaluacion.preguntas];
    
    document.getElementById('editEvalNombre').value = evaluacion.nombre;
    document.getElementById('editEvalDescripcion').value = evaluacion.descripcion || '';
    document.getElementById('editEvalTipo').value = evaluacion.tipo;
    document.getElementById('editEvalNivel').value = evaluacion.nivel;
    document.getElementById('editEvalDuracion').value = evaluacion.duracion || 90;
    
    actualizarContadorSeleccionEdicion();
    cargarListaPreguntasEdicion();
    
    const modal = document.getElementById('modalEdicionEvaluacion');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalEdicion() {
    const modal = document.getElementById('modalEdicionEvaluacion');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    evaluacionEditando = null;
    preguntasSeleccionadasEdicion = [];
}

// ==================== LISTA DE PREGUNTAS ====================

function cargarListaPreguntasCreacion() {
    preguntasFiltradasActuales = preguntasDisponibles.filter(p => p.estado === 'validada');
    aplicarFiltrosCreacionLocal();
    renderizarListaPreguntasCreacion();
}

function aplicarFiltrosCreacionLocal() {
    const nivel = document.getElementById('filtroNivelCreacion')?.value;
    const asignatura = document.getElementById('filtroAsignaturaCreacion')?.value;
    const dimension = document.getElementById('filtroDimensionCreacion')?.value;
    
    preguntasFiltradasActuales = preguntasDisponibles.filter(p => p.estado === 'validada');
    
    if (nivel) preguntasFiltradasActuales = preguntasFiltradasActuales.filter(p => p.nivel === nivel);
    if (asignatura) preguntasFiltradasActuales = preguntasFiltradasActuales.filter(p => p.asignatura === asignatura);
    if (dimension) preguntasFiltradasActuales = preguntasFiltradasActuales.filter(p => p.dimension === dimension);
}

function filtrarPreguntasCreacion() {
    aplicarFiltrosCreacionLocal();
    renderizarListaPreguntasCreacion();
    mostrarNotificacion(`${preguntasFiltradasActuales.length} preguntas encontradas`, 'info');
}

function limpiarFiltrosCreacion() {
    const selects = ['filtroNivelCreacion', 'filtroAsignaturaCreacion', 'filtroDimensionCreacion'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    aplicarFiltrosCreacionLocal();
    renderizarListaPreguntasCreacion();
}

function renderizarListaPreguntasCreacion() {
    const container = document.getElementById('listaPreguntasCreacion');
    if (!container) return;
    
    if (preguntasFiltradasActuales.length === 0) {
        container.innerHTML = `<div class="sin-resultados-lista" style="text-align: center; padding: 40px;"><i class="fas fa-inbox" style="font-size: 48px; color: #cbd5e1;"></i><p style="margin-top: 12px;">No hay preguntas disponibles</p></div>`;
        return;
    }
    
    container.innerHTML = preguntasFiltradasActuales.map(p => {
        const isSelected = preguntasSeleccionadas.includes(p.id);
        const preview = obtenerRespuestaPreview(p);
        
        return `
            <div class="pregunta-item-banco">
                <div class="pregunta-checkbox">
                    <input type="checkbox" class="pregunta-checkbox-creacion" data-id="${p.id}" ${isSelected ? 'checked' : ''}>
                </div>
                <div class="pregunta-contenido-banco">
                    <div class="pregunta-header-banco">
                        <span class="pregunta-id">#${p.id}</span>
                        <span class="badge-asignatura badge-${p.asignatura}">${getAsignaturaTexto(p.asignatura)}</span>
                        <span class="badge-tipo badge-${p.tipo}">${getTipoTexto(p.tipo)}</span>
                    </div>
                    <div class="pregunta-texto-banco">${escapeHtml(p.enunciado.substring(0, 100))}${p.enunciado.length > 100 ? '...' : ''}</div>
                    <div class="pregunta-respuesta-banco"><i class="fas fa-check-circle"></i> ${preview}</div>
                </div>
            </div>
        `;
    }).join('');
    
    document.querySelectorAll('.pregunta-checkbox-creacion').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = parseInt(this.dataset.id);
            if (this.checked) {
                if (!preguntasSeleccionadas.includes(id)) preguntasSeleccionadas.push(id);
            } else {
                preguntasSeleccionadas = preguntasSeleccionadas.filter(i => i !== id);
            }
            actualizarContadorSeleccion();
        });
    });
}

function cargarListaPreguntasEdicion() {
    preguntasFiltradasEdicion = preguntasDisponibles.filter(p => p.estado === 'validada');
    aplicarFiltrosEdicionLocal();
    renderizarListaPreguntasEdicion();
}

function aplicarFiltrosEdicionLocal() {
    const nivel = document.getElementById('filtroNivelEdicion')?.value;
    const asignatura = document.getElementById('filtroAsignaturaEdicion')?.value;
    
    preguntasFiltradasEdicion = preguntasDisponibles.filter(p => p.estado === 'validada');
    
    if (nivel) preguntasFiltradasEdicion = preguntasFiltradasEdicion.filter(p => p.nivel === nivel);
    if (asignatura) preguntasFiltradasEdicion = preguntasFiltradasEdicion.filter(p => p.asignatura === asignatura);
}

function filtrarPreguntasEdicion() {
    aplicarFiltrosEdicionLocal();
    renderizarListaPreguntasEdicion();
    mostrarNotificacion(`${preguntasFiltradasEdicion.length} preguntas encontradas`, 'info');
}

function limpiarFiltrosEdicion() {
    const selects = ['filtroNivelEdicion', 'filtroAsignaturaEdicion'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    aplicarFiltrosEdicionLocal();
    renderizarListaPreguntasEdicion();
}

function renderizarListaPreguntasEdicion() {
    const container = document.getElementById('listaPreguntasEdicion');
    if (!container) return;
    
    if (preguntasFiltradasEdicion.length === 0) {
        container.innerHTML = `<div class="sin-resultados-lista" style="text-align: center; padding: 40px;"><i class="fas fa-inbox" style="font-size: 48px; color: #cbd5e1;"></i><p style="margin-top: 12px;">No hay preguntas disponibles</p></div>`;
        return;
    }
    
    container.innerHTML = preguntasFiltradasEdicion.map(p => {
        const isSelected = preguntasSeleccionadasEdicion.includes(p.id);
        const preview = obtenerRespuestaPreview(p);
        
        return `
            <div class="pregunta-item-banco">
                <div class="pregunta-checkbox">
                    <input type="checkbox" class="pregunta-checkbox-edicion" data-id="${p.id}" ${isSelected ? 'checked' : ''}>
                </div>
                <div class="pregunta-contenido-banco">
                    <div class="pregunta-header-banco">
                        <span class="pregunta-id">#${p.id}</span>
                        <span class="badge-asignatura badge-${p.asignatura}">${getAsignaturaTexto(p.asignatura)}</span>
                        <span class="badge-tipo badge-${p.tipo}">${getTipoTexto(p.tipo)}</span>
                    </div>
                    <div class="pregunta-texto-banco">${escapeHtml(p.enunciado.substring(0, 100))}${p.enunciado.length > 100 ? '...' : ''}</div>
                    <div class="pregunta-respuesta-banco"><i class="fas fa-check-circle"></i> ${preview}</div>
                </div>
            </div>
        `;
    }).join('');
    
    document.querySelectorAll('.pregunta-checkbox-edicion').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = parseInt(this.dataset.id);
            if (this.checked) {
                if (!preguntasSeleccionadasEdicion.includes(id)) preguntasSeleccionadasEdicion.push(id);
            } else {
                preguntasSeleccionadasEdicion = preguntasSeleccionadasEdicion.filter(i => i !== id);
            }
            actualizarContadorSeleccionEdicion();
        });
    });
}

function seleccionarTodasCreacion() {
    preguntasSeleccionadas = [...new Set([...preguntasSeleccionadas, ...preguntasFiltradasActuales.map(p => p.id)])];
    renderizarListaPreguntasCreacion();
    actualizarContadorSeleccion();
    mostrarNotificacion(`${preguntasSeleccionadas.length} preguntas seleccionadas`, 'success');
}

function deseleccionarTodasCreacion() {
    const idsFiltrados = new Set(preguntasFiltradasActuales.map(p => p.id));
    preguntasSeleccionadas = preguntasSeleccionadas.filter(id => !idsFiltrados.has(id));
    renderizarListaPreguntasCreacion();
    actualizarContadorSeleccion();
}

function seleccionarTodasEdicion() {
    preguntasSeleccionadasEdicion = [...new Set([...preguntasSeleccionadasEdicion, ...preguntasFiltradasEdicion.map(p => p.id)])];
    renderizarListaPreguntasEdicion();
    actualizarContadorSeleccionEdicion();
    mostrarNotificacion(`${preguntasSeleccionadasEdicion.length} preguntas seleccionadas`, 'success');
}

function deseleccionarTodasEdicion() {
    const idsFiltrados = new Set(preguntasFiltradasEdicion.map(p => p.id));
    preguntasSeleccionadasEdicion = preguntasSeleccionadasEdicion.filter(id => !idsFiltrados.has(id));
    renderizarListaPreguntasEdicion();
    actualizarContadorSeleccionEdicion();
}

function actualizarContadorSeleccion() {
    const span = document.getElementById('preguntasSeleccionadasCount');
    if (span) span.textContent = preguntasSeleccionadas.length;
}

function actualizarContadorSeleccionEdicion() {
    const span = document.getElementById('preguntasSeleccionadasEdicionCount');
    if (span) span.textContent = preguntasSeleccionadasEdicion.length;
}

// ==================== GUARDAR EVALUACIONES ====================

function guardarEvaluacion(publicar) {
    const nombre = document.getElementById('evalNombre')?.value.trim();
    if (!nombre) {
        mostrarNotificacion('El nombre de la evaluación es requerido', 'error');
        return;
    }
    
    if (preguntasSeleccionadas.length === 0) {
        mostrarNotificacion('Debes seleccionar al menos una pregunta', 'error');
        return;
    }
    
    const asignaturas = [];
    const asignaturasSelect = document.getElementById('evalAsignaturas');
    if (asignaturasSelect) {
        Array.from(asignaturasSelect.selectedOptions).forEach(opt => asignaturas.push(opt.value));
    } else {
        asignaturas.push(document.getElementById('evalNivel')?.value || 'primaria');
    }
    
    const nuevaEvaluacion = {
        id: Date.now(),
        nombre: nombre,
        descripcion: document.getElementById('evalDescripcion')?.value || '',
        tipo: document.getElementById('evalTipo')?.value,
        estado: publicar ? 'publicada' : 'borrador',
        fechaCreacion: new Date().toLocaleDateString('es-ES'),
        fechaModificacion: new Date().toLocaleDateString('es-ES'),
        fechaPublicacion: publicar ? new Date().toLocaleDateString('es-ES') : (document.getElementById('evalFechaPublicacion')?.value || null),
        fechaVigencia: null,
        fechaProgramada: null,
        creador: "Usuario Actual",
        nivel: document.getElementById('evalNivel')?.value,
        asignaturas: asignaturas,
        preguntas: preguntasSeleccionadas,
        duracion: parseInt(document.getElementById('evalDuracion')?.value) || 90,
        publicada: publicar,
        borrador: !publicar,
        progreso: !publicar ? 100 : undefined
    };
    
    evaluacionesGlobales.push(nuevaEvaluacion);
    guardarEvaluaciones();
    
    cerrarModalCreacion();
    renderizarEvaluaciones();
    
    mostrarNotificacion(publicar ? 'Evaluación publicada exitosamente' : 'Evaluación guardada como borrador', 'success');
}

function actualizarEvaluacion() {
    if (!evaluacionEditando) return;
    
    if (preguntasSeleccionadasEdicion.length === 0) {
        mostrarNotificacion('Debes seleccionar al menos una pregunta', 'error');
        return;
    }
    
    const asignaturas = [];
    const asignaturasSelect = document.getElementById('editEvalAsignaturas');
    if (asignaturasSelect) {
        Array.from(asignaturasSelect.selectedOptions).forEach(opt => asignaturas.push(opt.value));
    } else {
        asignaturas.push(evaluacionEditando.nivel || 'primaria');
    }
    
    evaluacionEditando.nombre = document.getElementById('editEvalNombre').value;
    evaluacionEditando.descripcion = document.getElementById('editEvalDescripcion').value;
    evaluacionEditando.tipo = document.getElementById('editEvalTipo').value;
    evaluacionEditando.nivel = document.getElementById('editEvalNivel').value;
    evaluacionEditando.asignaturas = asignaturas;
    evaluacionEditando.preguntas = preguntasSeleccionadasEdicion;
    evaluacionEditando.duracion = parseInt(document.getElementById('editEvalDuracion').value) || 90;
    evaluacionEditando.fechaModificacion = new Date().toLocaleDateString('es-ES');
    
    const index = evaluacionesGlobales.findIndex(e => e.id === evaluacionEditando.id);
    if (index !== -1) {
        evaluacionesGlobales[index] = evaluacionEditando;
        guardarEvaluaciones();
    }
    
    cerrarModalEdicion();
    renderizarEvaluaciones();
    
    mostrarNotificacion('Evaluación actualizada correctamente', 'success');
}

// ==================== ACCIONES ====================

function publicarEvaluacion(id) {
    const evaluacion = evaluacionesGlobales.find(e => e.id === id);
    if (!evaluacion) return;
    
    if (evaluacion.publicada) {
        mostrarNotificacion('La evaluación ya está publicada', 'warning');
        return;
    }
    
    if (confirm(`¿Publicar la evaluación "${evaluacion.nombre}"? Una vez publicada no se podrá editar.`)) {
        evaluacion.publicada = true;
        evaluacion.borrador = false;
        evaluacion.estado = 'publicada';
        evaluacion.fechaPublicacion = new Date().toLocaleDateString('es-ES');
        
        guardarEvaluaciones();
        renderizarEvaluaciones();
        mostrarNotificacion('Evaluación publicada exitosamente', 'success');
    }
}

function programarEvaluacion(id) {
    const evaluacion = evaluacionesGlobales.find(e => e.id === id);
    if (!evaluacion) return;
    
    const fecha = prompt('Ingrese la fecha de programación (DD/MM/AAAA):', evaluacion.fechaProgramada || new Date().toLocaleDateString('es-ES'));
    if (fecha) {
        evaluacion.estado = 'programada';
        evaluacion.fechaProgramada = fecha;
        evaluacion.publicada = false;
        evaluacion.borrador = false;
        
        guardarEvaluaciones();
        renderizarEvaluaciones();
        mostrarNotificacion(`Evaluación programada para ${fecha}`, 'success');
    }
}

function verEvaluacionDetalle(id) {
    const evaluacion = evaluacionesGlobales.find(e => e.id === id);
    if (!evaluacion) return;
    
    const preguntasDetalle = evaluacion.preguntas.map(pid => preguntasDisponibles.find(p => p.id === pid)).filter(p => p);
    
    const detalleHTML = `
        <div class="modal-previsualizacion" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;">
            <div class="modal-contenido-previsualizacion" style="background: white; border-radius: 16px; max-width: 700px; width: 90%; max-height: 80vh; overflow: auto;">
                <div class="modal-header-previsualizacion" style="background: #691C32; color: white; padding: 20px; border-radius: 16px 16px 0 0; display: flex; justify-content: space-between;">
                    <h3 style="margin: 0;">${escapeHtml(evaluacion.nombre)}</h3>
                    <button class="btn-cerrar" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">✕</button>
                </div>
                <div class="modal-body-previsualizacion" style="padding: 20px;">
                    <p><strong>Descripción:</strong> ${escapeHtml(evaluacion.descripcion || 'Sin descripción')}</p>
                    <div style="display: flex; gap: 15px; flex-wrap: wrap; margin: 15px 0;">
                        <span><i class="fas fa-chart-line"></i> ${evaluacion.tipo === 'horizontal' ? 'Promoción Horizontal' : (evaluacion.tipo === 'vertical' ? 'Promoción Vertical' : 'Evaluación Diagnóstica')}</span>
                        <span><i class="fas fa-graduation-cap"></i> ${getNivelTexto(evaluacion.nivel)}</span>
                        <span><i class="fas fa-hourglass-half"></i> ${evaluacion.duracion} minutos</span>
                        <span><i class="fas fa-question-circle"></i> ${evaluacion.preguntas.length} preguntas</span>
                        <span><i class="fas fa-user"></i> Creador: ${escapeHtml(evaluacion.creador)}</span>
                    </div>
                    <h4>Listado de preguntas (${evaluacion.preguntas.length})</h4>
                    ${preguntasDetalle.map((p, i) => `
                        <div style="border: 1px solid #e9ecef; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                            <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                                <strong>${i+1}.</strong>
                                <span class="badge-asignatura badge-${p.asignatura}" style="font-size: 10px;">${getAsignaturaTexto(p.asignatura)}</span>
                                <span class="badge-tipo badge-${p.tipo}" style="font-size: 10px;">${getTipoTexto(p.tipo)}</span>
                            </div>
                            <div>${escapeHtml(p.enunciado)}</div>
                            <div style="margin-top: 8px; font-size: 13px; color: #27ae60;"><i class="fas fa-check-circle"></i> ${obtenerRespuestaPreview(p)}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-footer" style="padding: 15px 20px; border-top: 1px solid #e9ecef; text-align: right;">
                    <button class="btn btn-primary btn-cerrar">Cerrar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', detalleHTML);
    const modal = document.querySelector('.modal-previsualizacion');
    modal.querySelectorAll('.btn-cerrar').forEach(btn => {
        btn.addEventListener('click', () => modal.remove());
    });
    modal.addEventListener('click', function(e) {
        if (e.target === modal) modal.remove();
    });
}

function clonarEvaluacion(id) {
    const original = evaluacionesGlobales.find(e => e.id === id);
    if (!original) return;
    
    const nueva = {
        ...original,
        id: Date.now(),
        nombre: `${original.nombre} (Copia)`,
        estado: 'borrador',
        borrador: true,
        publicada: false,
        fechaCreacion: new Date().toLocaleDateString('es-ES'),
        fechaModificacion: new Date().toLocaleDateString('es-ES'),
        fechaPublicacion: null,
        progreso: 0
    };
    
    evaluacionesGlobales.push(nueva);
    guardarEvaluaciones();
    renderizarEvaluaciones();
    mostrarNotificacion('Evaluación clonada exitosamente', 'success');
}

// ==================== EVENTOS GLOBALES ====================

function inicializarEventosEvaluaciones() {
    const btnNueva = document.getElementById('btnNuevaEvaluacion');
    if (btnNueva) btnNueva.addEventListener('click', abrirModalCreacion);
    
    const btnNuevaCard = document.getElementById('btnNuevaEvaluacionCard');
    if (btnNuevaCard) btnNuevaCard.addEventListener('click', abrirModalCreacion);
    
    const filtroTipo = document.getElementById('filtroTipoEvaluacion');
    if (filtroTipo) filtroTipo.addEventListener('change', renderizarEvaluaciones);
    
    const filtroEstado = document.getElementById('filtroEstado');
    if (filtroEstado) filtroEstado.addEventListener('change', renderizarEvaluaciones);
    
    const buscador = document.getElementById('buscadorEvaluaciones');
    if (buscador) buscador.addEventListener('input', renderizarEvaluaciones);
}

// ==================== FUNCIONES AUXILIARES ====================

function getNivelTexto(nivel) {
    const niveles = { preescolar: 'Preescolar', primaria: 'Primaria', secundaria: 'Secundaria', media_superior: 'Media Superior' };
    return niveles[nivel] || nivel;
}

function getAsignaturaTexto(asignatura) {
    const map = { 
        espanol: 'Español', matematicas: 'Matemáticas', ciencias: 'Ciencias Naturales', 
        historia: 'Historia', geografia: 'Geografía', formacion_civica: 'Formación Cívica',
        artes: 'Artes', educacion_fisica: 'Educación Física', pedagogia: 'Pedagogía', 
        gestion: 'Gestión', tic: 'TIC', inclusion: 'Inclusión', didactica: 'Didáctica',
        vinculacion: 'Vinculación', disciplinar: 'Disciplinar'
    };
    return map[asignatura] || asignatura;
}

function getTipoTexto(tipo) {
    const tipos = { 
        opcion_multiple: 'Opción Múltiple', verdadero_falso: 'Verdadero/Falso',
        caso_practico: 'Caso Práctico', relacionar: 'Relacionar', completar: 'Completar' 
    };
    return tipos[tipo] || tipo;
}

function obtenerRespuestaPreview(pregunta) {
    if (pregunta.tipo === 'opcion_multiple') {
        const idx = parseInt(pregunta.respuesta_correcta);
        if (pregunta.opciones && pregunta.opciones[idx]) {
            return escapeHtml(pregunta.opciones[idx].substring(0, 40)) + (pregunta.opciones[idx].length > 40 ? '...' : '');
        }
        return 'Ver detalles';
    } else if (pregunta.tipo === 'verdadero_falso') {
        return pregunta.respuesta_correcta === 'true' ? 'Verdadero' : 'Falso';
    }
    return 'Ver detalles';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function mostrarNotificacion(mensaje, tipo = 'info') {
    // Usar la clase de notificación existente
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion-global notificacion-global-${tipo}`;
    notificacion.innerHTML = `
        <i class="fas ${tipo === 'success' ? 'fa-check-circle' : tipo === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${escapeHtml(mensaje)}</span>
        <button class="btn-cerrar-notificacion"><i class="fas fa-times"></i></button>
    `;
    document.body.appendChild(notificacion);
    
    setTimeout(() => notificacion.classList.add('mostrar'), 10);
    
    const cerrarBtn = notificacion.querySelector('.btn-cerrar-notificacion');
    cerrarBtn.addEventListener('click', () => {
        notificacion.classList.remove('mostrar');
        setTimeout(() => notificacion.remove(), 300);
    });
    
    setTimeout(() => {
        notificacion.classList.remove('mostrar');
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}