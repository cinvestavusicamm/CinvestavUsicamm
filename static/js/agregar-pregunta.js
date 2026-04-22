// Variables globales
let modal = null;
let currentMode = null;
let generatedQuestions = [];
let manualQuestions = [];
let preguntasGlobales = [];

// Preguntas de ejemplo iniciales
const preguntasIniciales = [
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
        opciones: [
            "Lectura en voz alta diaria",
            "Talleres de escritura creativa",
            "Círculos de lectura con padres",
            "Uso exclusivo de libros digitales"
        ],
        respuesta_correcta: "0",
        retroalimentacion: "Los círculos de lectura fomentan la participación activa y el gusto por la lectura."
    },
    {
        id: 2,
        enunciado: "Un docente observa que varios estudiantes tienen dificultades con fracciones. ¿Cuál sería la intervención más apropiada según el enfoque de la NEM?",
        asignatura: "matematicas",
        nivel: "secundaria",
        dimension: "didactica",
        tipo: "caso_practico",
        estado: "pendiente",
        fecha: "14/06/2024",
        bloom: "analizar",
        dificultad: "alta",
        opciones: [
            "Realizar una evaluación diagnóstica",
            "Implementar actividades con material concreto",
            "Trabajar en equipos colaborativos",
            "Utilizar recursos digitales interactivos"
        ],
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
    },
    {
        id: 4,
        enunciado: "Relaciona cada tipo de evaluación con su característica principal según la Nueva Escuela Mexicana.",
        asignatura: "evaluacion",
        nivel: "media_superior",
        dimension: "gestion",
        tipo: "relacionar",
        estado: "archivada",
        fecha: "12/06/2024",
        bloom: "comprender",
        dificultad: "media",
        opciones: [],
        respuesta_correcta: "",
        retroalimentacion: ""
    },
    {
        id: 5,
        enunciado: "Completa: La ___________ es fundamental para crear un ambiente inclusivo en el aula según los principios de la NEM.",
        asignatura: "inclusion",
        nivel: "primaria",
        dimension: "inclusion",
        tipo: "completar",
        estado: "rechazada",
        fecha: "11/06/2024",
        bloom: "aplicar",
        dificultad: "baja",
        opciones: [],
        respuesta_correcta: "diversidad",
        retroalimentacion: "La diversidad es un pilar fundamental para la inclusión educativa."
    }
];

// Esperar a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    cargarPreguntasDesdeStorage();
    inicializarModal();
    inicializarBotones();
    inicializarFiltros();
    inicializarAccionesTabla();
    actualizarEstadisticas();
});

// ==================== FUNCIONES DE ALMACENAMIENTO ====================

function cargarPreguntasDesdeStorage() {
    const stored = localStorage.getItem('escalafonia_preguntas');
    if (stored) {
        preguntasGlobales = JSON.parse(stored);
    } else {
        preguntasGlobales = [...preguntasIniciales];
        guardarPreguntasEnStorage();
    }
    renderizarTabla();
}

function guardarPreguntasEnStorage() {
    localStorage.setItem('escalafonia_preguntas', JSON.stringify(preguntasGlobales));
}

// ==================== FUNCIONES DE TABLA ====================

function renderizarTabla() {
    const tbody = document.querySelector('#tablaPreguntas tbody');
    if (!tbody) return;
    
    const filtros = obtenerFiltrosActivos();
    let preguntasFiltradas = filtrarPreguntas(preguntasGlobales, filtros);
    preguntasFiltradas.sort((a, b) => b.id - a.id);
    
    const itemsPorPagina = parseInt(document.getElementById('itemsPagina')?.value || 25);
    let paginaActual = 1;
    const paginaActiva = document.querySelector('.btn-paginacion.active');
    if (paginaActiva && !isNaN(parseInt(paginaActiva.textContent))) {
        paginaActual = parseInt(paginaActiva.textContent);
    }
    
    const inicio = (paginaActual - 1) * itemsPorPagina;
    const fin = inicio + itemsPorPagina;
    const paginadas = preguntasFiltradas.slice(inicio, fin);
    
    const totalRegistros = document.getElementById('totalRegistros');
    if (totalRegistros) totalRegistros.textContent = preguntasFiltradas.length;
    
    const contadorResultados = document.getElementById('contadorResultados');
    if (contadorResultados) {
        const mostrando = Math.min(paginadas.length, itemsPorPagina);
        contadorResultados.textContent = `Mostrando ${mostrando} de ${preguntasFiltradas.length} preguntas`;
    }
    
    actualizarPaginacion(preguntasFiltradas.length, itemsPorPagina, paginaActual);
    
    if (paginadas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 60px 20px;">
                    <i class="fas fa-inbox" style="font-size: 64px; color: #cbd5e1; margin-bottom: 16px; display: block;"></i>
                    <p style="color: #64748b; margin-bottom: 16px;">No hay preguntas que coincidan con los filtros</p>
                    <button class="btn btn-primary btn-sm" id="btnNuevaPreguntaEmpty">
                        <i class="fas fa-plus-circle"></i> Crear nueva pregunta
                    </button>
                </td>
            </tr>
        `;
        const btnEmpty = document.getElementById('btnNuevaPreguntaEmpty');
        if (btnEmpty) btnEmpty.addEventListener('click', abrirModal);
        return;
    }
    
    tbody.innerHTML = paginadas.map(pregunta => `
        <tr>
            <td>
                <input type="checkbox" class="select-row" data-id="${pregunta.id}">
            </td>
            <td>#${pregunta.id.toString().padStart(3, '0')}</td>
            <td>
                <div class="pregunta-enunciado">
                    <strong>${escapeHtml(pregunta.enunciado.length > 100 ? pregunta.enunciado.substring(0, 100) + '...' : pregunta.enunciado)}</strong>
                    <div class="pregunta-meta">
                        <span class="badge badge-sm badge-bloom badge-bloom-${pregunta.bloom || 'recordar'}">${getBloomTexto(pregunta.bloom)}</span>
                        <span class="badge badge-sm badge-dificultad">${getDificultadTexto(pregunta.dificultad)}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge-asignatura badge-${pregunta.asignatura}">${getAsignaturaTexto(pregunta.asignatura)}</span>
            </td>
            <td>${getNivelTexto(pregunta.nivel)}</td>
            <td>${getDimensionTexto(pregunta.dimension)}</td>
            <td>
                <span class="badge-tipo badge-${pregunta.tipo}">${getTipoTexto(pregunta.tipo)}</span>
            </td>
            <td>
                <span class="badge-estado badge-estado-${pregunta.estado}">${getEstadoTexto(pregunta.estado)}</span>
            </td>
            <td>${pregunta.fecha}</td>
            <td>
                <div class="acciones-tabla">
                    <button class="btn-icon btn-sm btn-editar-pregunta" title="Editar" data-id="${pregunta.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-ver-pregunta" title="Ver detalles" data-id="${pregunta.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-eliminar-pregunta" title="Eliminar" data-id="${pregunta.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    document.querySelectorAll('.btn-editar-pregunta').forEach(btn => {
        btn.addEventListener('click', () => editarPregunta(parseInt(btn.dataset.id)));
    });
    
    document.querySelectorAll('.btn-ver-pregunta').forEach(btn => {
        btn.addEventListener('click', () => verPregunta(parseInt(btn.dataset.id)));
    });
    
    document.querySelectorAll('.btn-eliminar-pregunta').forEach(btn => {
        btn.addEventListener('click', () => eliminarPregunta(parseInt(btn.dataset.id)));
    });
    
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.onclick = function() {
            document.querySelectorAll('.select-row').forEach(cb => cb.checked = this.checked);
        };
    }
}

function actualizarPaginacion(total, itemsPorPagina, paginaActual) {
    const totalPaginas = Math.ceil(total / itemsPorPagina);
    const paginacionContainer = document.querySelector('.paginacion-controls');
    if (!paginacionContainer) return;
    
    if (totalPaginas <= 1) {
        paginacionContainer.innerHTML = `
            <button class="btn-paginacion" disabled><i class="fas fa-chevron-left"></i></button>
            <button class="btn-paginacion active">1</button>
            <button class="btn-paginacion" disabled><i class="fas fa-chevron-right"></i></button>
        `;
        return;
    }
    
    let html = `
        <button class="btn-paginacion" data-page="prev" ${paginaActual === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    const maxBotones = 5;
    let inicio = Math.max(1, paginaActual - Math.floor(maxBotones / 2));
    let fin = Math.min(totalPaginas, inicio + maxBotones - 1);
    
    if (fin - inicio + 1 < maxBotones && inicio > 1) {
        inicio = Math.max(1, fin - maxBotones + 1);
    }
    
    if (inicio > 1) {
        html += `<button class="btn-paginacion" data-page="1">1</button>`;
        if (inicio > 2) html += `<span class="paginacion-ellipsis">...</span>`;
    }
    
    for (let i = inicio; i <= fin; i++) {
        html += `<button class="btn-paginacion ${i === paginaActual ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) html += `<span class="paginacion-ellipsis">...</span>`;
        html += `<button class="btn-paginacion" data-page="${totalPaginas}">${totalPaginas}</button>`;
    }
    
    html += `
        <button class="btn-paginacion" data-page="next" ${paginaActual === totalPaginas ? 'disabled' : ''}>
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    paginacionContainer.innerHTML = html;
    
    document.querySelectorAll('.btn-paginacion').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.disabled) return;
            const page = this.dataset.page;
            if (page === 'prev') {
                cambiarPagina(paginaActual - 1);
            } else if (page === 'next') {
                cambiarPagina(paginaActual + 1);
            } else {
                cambiarPagina(parseInt(page));
            }
        });
    });
    
    const jumpInput = document.querySelector('.jump-input');
    const jumpBtn = document.querySelector('.btn-jump');
    if (jumpInput && jumpBtn) {
        jumpInput.max = totalPaginas;
        jumpBtn.onclick = () => {
            let pagina = parseInt(jumpInput.value);
            if (isNaN(pagina)) pagina = 1;
            pagina = Math.max(1, Math.min(totalPaginas, pagina));
            cambiarPagina(pagina);
            jumpInput.value = pagina;
        };
    }
}

function cambiarPagina(pagina) {
    const btnAnterior = document.querySelector('.btn-paginacion.active');
    if (btnAnterior) btnAnterior.classList.remove('active');
    
    const nuevosBtns = document.querySelectorAll('.btn-paginacion');
    nuevosBtns.forEach(btn => {
        if (btn.textContent === pagina.toString()) {
            btn.classList.add('active');
        }
    });
    
    renderizarTabla();
}

// ==================== FUNCIONES DE FILTROS ====================

function obtenerFiltrosActivos() {
    const nivel = Array.from(document.getElementById('filtroNivel')?.selectedOptions || []).map(opt => opt.value);
    const asignatura = Array.from(document.getElementById('filtroAsignatura')?.selectedOptions || []).map(opt => opt.value);
    const dimension = Array.from(document.getElementById('filtroDimension')?.selectedOptions || []).map(opt => opt.value);
    const estado = document.getElementById('filtroEstado')?.value;
    const tipo = Array.from(document.getElementById('filtroTipo')?.selectedOptions || []).map(opt => opt.value);
    const fechaDesde = document.getElementById('filtroFechaDesde')?.value;
    const fechaHasta = document.getElementById('filtroFechaHasta')?.value;
    
    return { nivel, asignatura, dimension, estado, tipo, fechaDesde, fechaHasta };
}

function filtrarPreguntas(preguntas, filtros) {
    return preguntas.filter(p => {
        if (filtros.nivel.length > 0 && filtros.nivel[0] !== '' && !filtros.nivel.includes(p.nivel)) return false;
        if (filtros.asignatura.length > 0 && filtros.asignatura[0] !== '' && !filtros.asignatura.includes(p.asignatura)) return false;
        if (filtros.dimension.length > 0 && filtros.dimension[0] !== '' && !filtros.dimension.includes(p.dimension)) return false;
        if (filtros.estado && filtros.estado !== 'todas' && p.estado !== filtros.estado) return false;
        if (filtros.tipo.length > 0 && filtros.tipo[0] !== '' && !filtros.tipo.includes(p.tipo)) return false;
        
        if (filtros.fechaDesde) {
            const [dia, mes, anio] = p.fecha.split('/');
            const fechaPregunta = `${anio}-${mes}-${dia}`;
            if (fechaPregunta < filtros.fechaDesde) return false;
        }
        if (filtros.fechaHasta) {
            const [dia, mes, anio] = p.fecha.split('/');
            const fechaPregunta = `${anio}-${mes}-${dia}`;
            if (fechaPregunta > filtros.fechaHasta) return false;
        }
        
        return true;
    });
}

function inicializarFiltros() {
    const toggleFiltros = document.getElementById('toggleFiltros');
    const contenidoFiltros = document.getElementById('contenidoFiltros');
    
    if (toggleFiltros && contenidoFiltros) {
        contenidoFiltros.classList.add('collapsed');
        toggleFiltros.classList.add('collapsed');
        
        toggleFiltros.addEventListener('click', function() {
            contenidoFiltros.classList.toggle('collapsed');
            this.classList.toggle('collapsed');
        });
    }
    
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    
    if (btnAplicarFiltros) btnAplicarFiltros.addEventListener('click', aplicarFiltros);
    if (btnLimpiarFiltros) btnLimpiarFiltros.addEventListener('click', limpiarFiltros);
}

function aplicarFiltros() {
    const filtros = obtenerFiltrosActivos();
    let filtrosActivos = 0;
    
    if (filtros.nivel.length > 0 && filtros.nivel[0] !== '') filtrosActivos += filtros.nivel.length;
    if (filtros.asignatura.length > 0 && filtros.asignatura[0] !== '') filtrosActivos += filtros.asignatura.length;
    if (filtros.dimension.length > 0 && filtros.dimension[0] !== '') filtrosActivos += filtros.dimension.length;
    if (filtros.estado && filtros.estado !== 'todas') filtrosActivos++;
    if (filtros.tipo.length > 0 && filtros.tipo[0] !== '') filtrosActivos += filtros.tipo.length;
    if (filtros.fechaDesde) filtrosActivos++;
    if (filtros.fechaHasta) filtrosActivos++;
    
    const contador = document.getElementById('contadorFiltros');
    if (contador) contador.textContent = filtrosActivos;
    
    renderizarTabla();
    mostrarNotificacion('Filtros aplicados correctamente', 'success');
}

function limpiarFiltros() {
    const filtroNivel = document.getElementById('filtroNivel');
    if (filtroNivel) Array.from(filtroNivel.options).forEach(opt => opt.selected = false);
    
    const filtroAsignatura = document.getElementById('filtroAsignatura');
    if (filtroAsignatura) Array.from(filtroAsignatura.options).forEach(opt => opt.selected = false);
    
    const filtroDimension = document.getElementById('filtroDimension');
    if (filtroDimension) Array.from(filtroDimension.options).forEach(opt => opt.selected = false);
    
    const filtroTipo = document.getElementById('filtroTipo');
    if (filtroTipo) Array.from(filtroTipo.options).forEach(opt => opt.selected = false);
    
    const filtroEstado = document.getElementById('filtroEstado');
    if (filtroEstado) filtroEstado.value = 'todas';
    
    const filtroFechaDesde = document.getElementById('filtroFechaDesde');
    if (filtroFechaDesde) filtroFechaDesde.value = '';
    
    const filtroFechaHasta = document.getElementById('filtroFechaHasta');
    if (filtroFechaHasta) filtroFechaHasta.value = '';
    
    const contador = document.getElementById('contadorFiltros');
    if (contador) contador.textContent = '0';
    
    renderizarTabla();
    mostrarNotificacion('Filtros limpiados', 'info');
}

// ==================== FUNCIONES DE ACCIONES DE TABLA ====================

function inicializarAccionesTabla() {
    const refreshBtn = document.getElementById('refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            cargarPreguntasDesdeStorage();
            mostrarNotificacion('Tabla actualizada', 'success');
        });
    }
    
    const exportBtn = document.getElementById('exportjson');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            const filtros = obtenerFiltrosActivos();
            const preguntasFiltradas = filtrarPreguntas(preguntasGlobales, filtros);
            exportarAJSON(preguntasFiltradas);
        });
    }
    
    const itemsPagina = document.getElementById('itemsPagina');
    if (itemsPagina) {
        itemsPagina.addEventListener('change', function() {
            cambiarPagina(1);
            renderizarTabla();
        });
    }
    
    const buscador = document.getElementById('buscadorPreguntas');
    if (buscador) {
        buscador.addEventListener('input', function() {
            buscarPreguntas(this.value);
        });
    }
}

function buscarPreguntas(texto) {
    if (!texto.trim()) {
        renderizarTabla();
        return;
    }
    
    const preguntasFiltradas = preguntasGlobales.filter(p => 
        p.enunciado.toLowerCase().includes(texto.toLowerCase())
    );
    
    renderizarTablaConPreguntas(preguntasFiltradas);
}

function renderizarTablaConPreguntas(preguntas) {
    const tbody = document.querySelector('#tablaPreguntas tbody');
    if (!tbody) return;
    
    if (preguntas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 60px 20px;">
                    <i class="fas fa-search" style="font-size: 64px; color: #cbd5e1; margin-bottom: 16px; display: block;"></i>
                    <p style="color: #64748b;">No se encontraron preguntas para "${escapeHtml(texto)}"</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = preguntas.map(pregunta => `
        <tr>
            <td><input type="checkbox" class="select-row" data-id="${pregunta.id}"></td>
            <td>#${pregunta.id.toString().padStart(3, '0')}</td>
            <td>
                <div class="pregunta-enunciado">
                    <strong>${escapeHtml(pregunta.enunciado.length > 100 ? pregunta.enunciado.substring(0, 100) + '...' : pregunta.enunciado)}</strong>
                    <div class="pregunta-meta">
                        <span class="badge badge-sm badge-bloom badge-bloom-${pregunta.bloom || 'recordar'}">${getBloomTexto(pregunta.bloom)}</span>
                        <span class="badge badge-sm badge-dificultad">${getDificultadTexto(pregunta.dificultad)}</span>
                    </div>
                </div>
            </td>
            <td><span class="badge-asignatura badge-${pregunta.asignatura}">${getAsignaturaTexto(pregunta.asignatura)}</span></td>
            <td>${getNivelTexto(pregunta.nivel)}</td>
            <td>${getDimensionTexto(pregunta.dimension)}</td>
            <td><span class="badge-tipo badge-${pregunta.tipo}">${getTipoTexto(pregunta.tipo)}</span></td>
            <td><span class="badge-estado badge-estado-${pregunta.estado}">${getEstadoTexto(pregunta.estado)}</span></td>
            <td>${pregunta.fecha}</td>
            <td>
                <div class="acciones-tabla">
                    <button class="btn-icon btn-sm btn-editar-pregunta" title="Editar" data-id="${pregunta.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-ver-pregunta" title="Ver detalles" data-id="${pregunta.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-eliminar-pregunta" title="Eliminar" data-id="${pregunta.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    document.querySelectorAll('.btn-editar-pregunta').forEach(btn => {
        btn.addEventListener('click', () => editarPregunta(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll('.btn-ver-pregunta').forEach(btn => {
        btn.addEventListener('click', () => verPregunta(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll('.btn-eliminar-pregunta').forEach(btn => {
        btn.addEventListener('click', () => eliminarPregunta(parseInt(btn.dataset.id)));
    });
}

function exportarAJSON(preguntas) {
    const dataStr = JSON.stringify(preguntas, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `preguntas_${new Date().toISOString().slice(0,19)}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    mostrarNotificacion(`${preguntas.length} preguntas exportadas correctamente`, 'success');
}

function editarPregunta(id) {
    const pregunta = preguntasGlobales.find(p => p.id === id);
    if (pregunta) {
        mostrarNotificacion(`Editando: ${pregunta.enunciado.substring(0, 50)}...`, 'info');
    }
}

function verPregunta(id) {
    const pregunta = preguntasGlobales.find(p => p.id === id);
    if (pregunta) {
        mostrarNotificacion(`Pregunta #${id}: ${pregunta.enunciado.substring(0, 80)}...`, 'info');
    }
}

function eliminarPregunta(id) {
    if (confirm('¿Estás seguro de que deseas eliminar esta pregunta? Esta acción no se puede deshacer.')) {
        preguntasGlobales = preguntasGlobales.filter(p => p.id !== id);
        guardarPreguntasEnStorage();
        renderizarTabla();
        actualizarEstadisticas();
        mostrarNotificacion('Pregunta eliminada correctamente', 'success');
    }
}

function actualizarEstadisticas() {
    const total = preguntasGlobales.length;
    const validadas = preguntasGlobales.filter(p => p.estado === 'validada').length;
    const pendientes = preguntasGlobales.filter(p => p.estado === 'pendiente').length;
    const rechazadas = preguntasGlobales.filter(p => p.estado === 'rechazada').length;
    
    const totalElement = document.querySelector('.estadistica-item:first-child .estadistica-contenido h3');
    const validadasElement = document.querySelector('.estadistica-item:nth-child(2) .estadistica-contenido h3');
    const pendientesElement = document.querySelector('.estadistica-item:nth-child(3) .estadistica-contenido h3');
    const rechazadasElement = document.querySelector('.estadistica-item:nth-child(4) .estadistica-contenido h3');
    
    if (totalElement) totalElement.textContent = total.toLocaleString();
    if (validadasElement) validadasElement.textContent = validadas.toLocaleString();
    if (pendientesElement) pendientesElement.textContent = pendientes.toLocaleString();
    if (rechazadasElement) rechazadasElement.textContent = rechazadas.toLocaleString();
}

function agregarPreguntasATabla(preguntas) {
    let nuevoId = preguntasGlobales.length > 0 ? Math.max(...preguntasGlobales.map(p => p.id)) + 1 : 6;
    const fechaActual = new Date().toLocaleDateString('es-ES');
    
    preguntas.forEach(p => {
        preguntasGlobales.push({
            ...p,
            id: nuevoId++,
            fecha: fechaActual,
            estado: p.estado || 'pendiente'
        });
    });
    
    guardarPreguntasEnStorage();
    renderizarTabla();
    actualizarEstadisticas();
    mostrarNotificacion(`${preguntas.length} pregunta(s) agregada(s) al banco`, 'success');
}

// ==================== MODAL AGREGAR PREGUNTA ====================

function inicializarModal() {
    const modalHTML = `
        <div id="modalAgregarPregunta" class="modal-agregar-pregunta">
            <div class="modal-contenido">
                <div class="modal-header">
                    <h2><i class="fas fa-plus-circle"></i> Agregar Nueva Pregunta</h2>
                    <button class="btn-cerrar-modal" id="cerrarModalBtn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div id="panelSeleccion" class="panel-seleccion">
                        <div class="opcion-creacion" data-modo="manual">
                            <div class="opcion-icono">
                                <i class="fas fa-pen-alt"></i>
                            </div>
                            <h3>Crear Pregunta Manualmente</h3>
                            <p>Diseña tus propias preguntas con control total sobre cada detalle.</p>
                            <ul class="opcion-caracteristicas">
                                <li><i class="fas fa-check-circle"></i> Control total del contenido</li>
                                <li><i class="fas fa-check-circle"></i> Múltiples formatos disponibles</li>
                                <li><i class="fas fa-check-circle"></i> Ajuste preciso de dificultad</li>
                            </ul>
                        </div>
                        <div class="opcion-creacion" data-modo="ia">
                            <div class="opcion-icono">
                                <i class="fas fa-robot"></i>
                            </div>
                            <h3>Generar con IA</h3>
                            <p>Utiliza inteligencia artificial para crear preguntas automáticamente.</p>
                            <ul class="opcion-caracteristicas">
                                <li><i class="fas fa-check-circle"></i> Generación masiva de preguntas</li>
                                <li><i class="fas fa-check-circle"></i> Basado en estándares educativos</li>
                                <li><i class="fas fa-check-circle"></i> Ahorra tiempo de diseño</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div id="panelManual" class="panel-creacion" style="display: none;">
                        <div class="panel-header">
                            <button class="btn-volver" id="volverManualBtn">
                                <i class="fas fa-arrow-left"></i> Volver
                            </button>
                            <h3><i class="fas fa-pen-alt"></i> Crear Pregunta Manualmente</h3>
                        </div>
                        
                        <form id="formManualPregunta" class="form-manual">
                            <div class="form-grid">
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-hashtag"></i> Cantidad de Preguntas</label>
                                    <input type="number" id="cantidadManual" min="1" max="20" value="1" class="form-control">
                                    <small>Máximo 20 preguntas por lote</small>
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-clock"></i> Tiempo Estimado (minutos)</label>
                                    <input type="number" id="tiempoManual" min="1" max="180" value="30" class="form-control">
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-tag"></i> Tema / Área Temática</label>
                                    <input type="text" id="temaManual" placeholder="Ej: Fracciones, Lectura crítica..." class="form-control">
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-align-left"></i> Descripción / Contexto</label>
                                    <textarea id="descripcionManual" rows="3" placeholder="Describe el contexto de la evaluación..." class="form-control"></textarea>
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-graduation-cap"></i> Nivel Educativo</label>
                                    <select id="nivelManual" class="form-control">
                                        <option value="preescolar">Preescolar</option>
                                        <option value="primaria" selected>Primaria</option>
                                        <option value="secundaria">Secundaria</option>
                                        <option value="media_superior">Media Superior</option>
                                    </select>
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-book"></i> Asignatura</label>
                                    <select id="asignaturaManual" class="form-control">
                                        <option value="espanol">Español</option>
                                        <option value="matematicas" selected>Matemáticas</option>
                                        <option value="ciencias">Ciencias Naturales</option>
                                        <option value="historia">Historia</option>
                                        <option value="geografia">Geografía</option>
                                        <option value="formacion_civica">Formación Cívica</option>
                                        <option value="artes">Artes</option>
                                        <option value="educacion_fisica">Educación Física</option>
                                    </select>
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-layer-group"></i> Dimensión</label>
                                    <select id="dimensionManual" class="form-control">
                                        <option value="pedagogica">Pedagógica</option>
                                        <option value="disciplinar">Disciplinar</option>
                                        <option value="didactica">Didáctica</option>
                                        <option value="gestion">Gestión Escolar</option>
                                        <option value="tic">Tecnologías (TIC)</option>
                                        <option value="vinculacion">Vinculación</option>
                                        <option value="inclusion">Inclusión</option>
                                    </select>
                                </div>
                                <div class="grupo-formulario">
                                    <label><i class="fas fa-question-circle"></i> Tipo de Pregunta</label>
                                    <select id="tipoManual" class="form-control">
                                        <option value="opcion_multiple">Opción Múltiple</option>
                                        <option value="verdadero_falso">Verdadero/Falso</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="grupo-botones">
                                <button type="button" class="btn btn-primary" id="continuarManualBtn">
                                    <i class="fas fa-arrow-right"></i> Continuar
                                </button>
                                <button type="button" class="btn btn-secondary" id="cancelarManualBtn">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <div id="panelManualDetalle" class="panel-creacion" style="display: none;">
                        <div class="panel-header">
                            <button class="btn-volver" id="volverManualConfigBtn">
                                <i class="fas fa-arrow-left"></i> Volver
                            </button>
                            <h3><i class="fas fa-edit"></i> Detalle de Preguntas</h3>
                        </div>
                        <div id="preguntasManualContainer" class="preguntas-container"></div>
                        <div class="grupo-botones">
                            <button type="button" class="btn btn-primary" id="guardarManualPreguntasBtn">
                                <i class="fas fa-save"></i> Guardar Preguntas
                            </button>
                            <button type="button" class="btn btn-secondary" id="cancelarManualDetalleBtn">
                                <i class="fas fa-times"></i> Cancelar
                            </button>
                        </div>
                    </div>
                    
                    <div id="panelIA" class="panel-creacion" style="display: none;">
                        <div class="panel-header">
                            <button class="btn-volver" id="volverIABtn">
                                <i class="fas fa-arrow-left"></i> Volver
                            </button>
                            <h3><i class="fas fa-robot"></i> Generar Preguntas con IA</h3>
                        </div>
                        
                        <div class="contenedor-generador-ia">
                            <div class="panel-configuracion-ia">
                                <div class="panel-header-ia">
                                    <h4><i class="fas fa-cogs"></i> Configuración de Parámetros</h4>
                                    <p class="panel-subtitulo">Define los criterios para la generación de preguntas</p>
                                </div>
                                
                                <form id="formGeneradorIA" class="form-generador-ia">
                                    <div class="grupo-formulario-ia">
                                        <label for="cantidadIA"><i class="fas fa-hashtag"></i> Cantidad de Preguntas</label>
                                        <div class="input-con-icono">
                                            <i class="fas fa-list-ol"></i>
                                            <input type="number" id="cantidadIA" min="1" max="50" value="5">
                                        </div>
                                        <small>Máximo 50 preguntas por solicitud</small>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label for="nivelIA"><i class="fas fa-graduation-cap"></i> Nivel Educativo</label>
                                        <div class="select-con-icono">
                                            <i class="fas fa-school"></i>
                                            <select id="nivelIA">
                                                <option value="">Seleccionar nivel</option>
                                                <option value="preescolar">Preescolar</option>
                                                <option value="primaria" selected>Primaria</option>
                                                <option value="secundaria">Secundaria</option>
                                                <option value="media_superior">Media Superior</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label for="asignaturaIA"><i class="fas fa-book"></i> Asignatura / Área</label>
                                        <div class="select-con-icono">
                                            <i class="fas fa-book-open"></i>
                                            <select id="asignaturaIA">
                                                <option value="">Seleccionar asignatura</option>
                                                <option value="espanol">Español</option>
                                                <option value="matematicas" selected>Matemáticas</option>
                                                <option value="ciencias">Ciencias Naturales</option>
                                                <option value="historia">Historia</option>
                                                <option value="geografia">Geografía</option>
                                                <option value="formacion_civica">Formación Cívica y Ética</option>
                                                <option value="artes">Artes</option>
                                                <option value="educacion_fisica">Educación Física</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label for="dimensionIA"><i class="fas fa-layer-group"></i> Dimensión de Evaluación</label>
                                        <div class="select-con-icono">
                                            <i class="fas fa-chart-pie"></i>
                                            <select id="dimensionIA">
                                                <option value="">Seleccionar dimensión</option>
                                                <option value="pedagogica" selected>Pedagógica</option>
                                                <option value="disciplinar">Disciplinar</option>
                                                <option value="didactica">Didáctica</option>
                                                <option value="gestion">Gestión Escolar</option>
                                                <option value="tic">Tecnologías de la Información</option>
                                                <option value="vinculacion">Vinculación Comunitaria</option>
                                                <option value="inclusion">Inclusión Educativa</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label><i class="fas fa-question-circle"></i> Tipos de Pregunta</label>
                                        <div class="tipos-checkbox-group">
                                            <label class="checkbox-option">
                                                <input type="checkbox" value="opcion_multiple" checked> Opción Múltiple
                                            </label>
                                            <label class="checkbox-option">
                                                <input type="checkbox" value="verdadero_falso"> Verdadero/Falso
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label for="bloomIA"><i class="fas fa-brain"></i> Nivel de Bloom</label>
                                        <div class="select-con-icono">
                                            <i class="fas fa-chart-line"></i>
                                            <select id="bloomIA">
                                                <option value="recordar">Recordar</option>
                                                <option value="comprender" selected>Comprender</option>
                                                <option value="aplicar">Aplicar</option>
                                                <option value="analizar">Analizar</option>
                                                <option value="evaluar">Evaluar</option>
                                                <option value="crear">Crear</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-formulario-ia">
                                        <label for="instruccionesIA"><i class="fas fa-comment-dots"></i> Instrucciones Específicas</label>
                                        <div class="textarea-con-icono">
                                            <i class="fas fa-edit"></i>
                                            <textarea id="instruccionesIA" rows="3" 
                                                placeholder="Escribe instrucciones adicionales para la IA..."></textarea>
                                        </div>
                                    </div>
                                    
                                    <div class="grupo-botones-ia">
                                        <button type="button" class="btn btn-primary btn-generar-ia" id="generarIABtn">
                                            <i class="fas fa-magic"></i> Generar Preguntas con IA
                                        </button>
                                        <button type="button" class="btn btn-secondary btn-limpiar-ia" id="limpiarIAFormBtn">
                                            <i class="fas fa-eraser"></i> Limpiar
                                        </button>
                                    </div>
                                </form>
                            </div>
                            
                            <div class="panel-previa-ia">
                                <div class="panel-header-ia">
                                    <h4><i class="fas fa-eye"></i> Vista Previa y Resultados</h4>
                                    <p class="panel-subtitulo">Las preguntas generadas aparecerán aquí. Puedes editar o eliminar cada pregunta.</p>
                                </div>
                                
                                <div class="estado-generador-ia" id="estadoGeneradorIA">
                                    <div class="estado-icono-ia">
                                        <i class="fas fa-robot"></i>
                                    </div>
                                    <div class="estado-contenido-ia">
                                        <h3>Listo para generar</h3>
                                        <p>Configura los parámetros y haz clic en "Generar Preguntas con IA"</p>
                                    </div>
                                </div>
                                
                                <div class="contenedor-preguntas-ia" id="contenedorPreguntasIA" style="display: none;"></div>
                                
                                <div class="acciones-preguntas-ia" id="accionesPreguntasIA" style="display: none;">
                                    <div class="contador-preguntas-ia">
                                        <span id="contadorPreguntasIA">0</span> preguntas generadas
                                    </div>
                                    <div class="botones-acciones-ia">
                                        <button class="btn btn-success" id="enviarValidacionIABtn">
                                            <i class="fas fa-paper-plane"></i> Enviar a Validación
                                        </button>
                                        <button class="btn btn-outline" id="descargarIABtn">
                                            <i class="fas fa-download"></i> Descargar JSON
                                        </button>
                                        <button class="btn btn-outline btn-danger" id="desecharIABtn">
                                            <i class="fas fa-trash-alt"></i> Desechar Todo
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    modal = document.getElementById('modalAgregarPregunta');
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) cerrarModal();
    });
}

function inicializarBotones() {
    const btnNuevaPregunta = document.getElementById('btnNuevaPregunta');
    if (btnNuevaPregunta) btnNuevaPregunta.addEventListener('click', abrirModal);
    
    const cerrarBtn = document.getElementById('cerrarModalBtn');
    if (cerrarBtn) cerrarBtn.addEventListener('click', cerrarModal);
    
    const opciones = document.querySelectorAll('.opcion-creacion');
    opciones.forEach(opcion => {
        opcion.addEventListener('click', function() {
            const modo = this.dataset.modo;
            if (modo === 'manual') mostrarPanelManual();
            else if (modo === 'ia') mostrarPanelIA();
        });
    });
    
    const volverManualBtn = document.getElementById('volverManualBtn');
    if (volverManualBtn) volverManualBtn.addEventListener('click', mostrarPanelSeleccion);
    
    const volverManualConfigBtn = document.getElementById('volverManualConfigBtn');
    if (volverManualConfigBtn) volverManualConfigBtn.addEventListener('click', mostrarPanelManual);
    
    const volverIABtn = document.getElementById('volverIABtn');
    if (volverIABtn) volverIABtn.addEventListener('click', mostrarPanelSeleccion);
    
    const continuarManualBtn = document.getElementById('continuarManualBtn');
    if (continuarManualBtn) continuarManualBtn.addEventListener('click', mostrarFormularioPreguntasManual);
    
    const cancelarManualBtn = document.getElementById('cancelarManualBtn');
    if (cancelarManualBtn) cancelarManualBtn.addEventListener('click', cerrarModal);
    
    const cancelarManualDetalleBtn = document.getElementById('cancelarManualDetalleBtn');
    if (cancelarManualDetalleBtn) cancelarManualDetalleBtn.addEventListener('click', cerrarModal);
    
    const guardarManualPreguntasBtn = document.getElementById('guardarManualPreguntasBtn');
    if (guardarManualPreguntasBtn) guardarManualPreguntasBtn.addEventListener('click', guardarPreguntasManuales);
    
    const generarIABtn = document.getElementById('generarIABtn');
    if (generarIABtn) generarIABtn.addEventListener('click', generarPreguntasIA);
    
    const limpiarIAFormBtn = document.getElementById('limpiarIAFormBtn');
    if (limpiarIAFormBtn) limpiarIAFormBtn.addEventListener('click', limpiarFormularioIA);
    
    const enviarValidacionIABtn = document.getElementById('enviarValidacionIABtn');
    if (enviarValidacionIABtn) enviarValidacionIABtn.addEventListener('click', enviarPreguntasIAValidacion);
    
    const descargarIABtn = document.getElementById('descargarIABtn');
    if (descargarIABtn) descargarIABtn.addEventListener('click', descargarPreguntasIA);
    
    const desecharIABtn = document.getElementById('desecharIABtn');
    if (desecharIABtn) desecharIABtn.addEventListener('click', desecharPreguntasIA);
}

function abrirModal() {
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        mostrarPanelSeleccion();
    }
}

function cerrarModal() {
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        resetModal();
    }
}

function resetModal() {
    mostrarPanelSeleccion();
    
    const formManual = document.getElementById('formManualPregunta');
    if (formManual) formManual.reset();
    
    const formIA = document.getElementById('formGeneradorIA');
    if (formIA) formIA.reset();
    
    generatedQuestions = [];
    manualQuestions = [];
    
    const contenedorPreguntasIA = document.getElementById('contenedorPreguntasIA');
    if (contenedorPreguntasIA) contenedorPreguntasIA.style.display = 'none';
    
    const estadoGeneradorIA = document.getElementById('estadoGeneradorIA');
    if (estadoGeneradorIA) estadoGeneradorIA.style.display = 'flex';
    
    const accionesPreguntasIA = document.getElementById('accionesPreguntasIA');
    if (accionesPreguntasIA) accionesPreguntasIA.style.display = 'none';
    
    const tipoCheckboxes = document.querySelectorAll('#formGeneradorIA input[type="checkbox"]');
    tipoCheckboxes.forEach(cb => cb.checked = cb.value === 'opcion_multiple');
}

function mostrarPanelSeleccion() {
    const panelSeleccion = document.getElementById('panelSeleccion');
    const panelManual = document.getElementById('panelManual');
    const panelManualDetalle = document.getElementById('panelManualDetalle');
    const panelIA = document.getElementById('panelIA');
    
    if (panelSeleccion) panelSeleccion.style.display = 'grid';
    if (panelManual) panelManual.style.display = 'none';
    if (panelManualDetalle) panelManualDetalle.style.display = 'none';
    if (panelIA) panelIA.style.display = 'none';
}

function mostrarPanelManual() {
    const panelSeleccion = document.getElementById('panelSeleccion');
    const panelManual = document.getElementById('panelManual');
    const panelManualDetalle = document.getElementById('panelManualDetalle');
    const panelIA = document.getElementById('panelIA');
    
    if (panelSeleccion) panelSeleccion.style.display = 'none';
    if (panelManual) panelManual.style.display = 'block';
    if (panelManualDetalle) panelManualDetalle.style.display = 'none';
    if (panelIA) panelIA.style.display = 'none';
}

function mostrarPanelIA() {
    const panelSeleccion = document.getElementById('panelSeleccion');
    const panelManual = document.getElementById('panelManual');
    const panelManualDetalle = document.getElementById('panelManualDetalle');
    const panelIA = document.getElementById('panelIA');
    
    if (panelSeleccion) panelSeleccion.style.display = 'none';
    if (panelManual) panelManual.style.display = 'none';
    if (panelManualDetalle) panelManualDetalle.style.display = 'none';
    if (panelIA) panelIA.style.display = 'block';
}

function mostrarFormularioPreguntasManual() {
    const cantidad = parseInt(document.getElementById('cantidadManual').value) || 1;
    const tema = document.getElementById('temaManual').value || 'General';
    const tipo = document.getElementById('tipoManual').value;
    
    const container = document.getElementById('preguntasManualContainer');
    if (!container) return;
    
    let html = `
        <div class="info-configuracion">
            <div class="info-badge"><i class="fas fa-info-circle"></i><span>Tema: ${escapeHtml(tema)}</span></div>
            <div class="info-badge"><i class="fas fa-layer-group"></i><span>Tipo: ${getTipoTexto(tipo)}</span></div>
        </div>
        <div class="preguntas-lista">
    `;
    
    for (let i = 0; i < cantidad; i++) {
        html += `
            <div class="pregunta-item-manual" data-index="${i}">
                <div class="pregunta-header-manual">
                    <h4>Pregunta ${i + 1}</h4>
                    <button type="button" class="btn-icon btn-eliminar-pregunta" data-index="${i}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
                <div class="pregunta-contenido-manual">
                    <div class="grupo-formulario">
                        <label>Enunciado de la pregunta <span class="required">*</span></label>
                        <textarea class="pregunta-enunciado-input" rows="2" placeholder="Escribe el enunciado de la pregunta..."></textarea>
                    </div>
                    <div class="grupo-formulario">
                        <label>Opciones de respuesta <span class="required">*</span></label>
                        <div class="opciones-container-manual">
        `;
        
        if (tipo === 'opcion_multiple') {
            for (let j = 0; j < 4; j++) {
                html += `
                    <div class="opcion-item-manual">
                        <input type="radio" name="correcta_${i}" value="${j}" class="opcion-correcta-radio">
                        <input type="text" class="opcion-texto-input" placeholder="Opción ${String.fromCharCode(65 + j)}">
                    </div>
                `;
            }
            html += `<small class="ayuda-texto">Selecciona el radio button de la opción correcta</small>`;
        } else if (tipo === 'verdadero_falso') {
            html += `
                <div class="opciones-vf">
                    <label class="opcion-vf"><input type="radio" name="correcta_${i}" value="true"> Verdadero</label>
                    <label class="opcion-vf"><input type="radio" name="correcta_${i}" value="false"> Falso</label>
                </div>
            `;
        }
        
        html += `
                        </div>
                    </div>
                    <div class="grupo-formulario">
                        <label>Retroalimentación / Explicación</label>
                        <textarea class="retroalimentacion-input" rows="2" placeholder="Explica por qué la respuesta es correcta..."></textarea>
                    </div>
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    container.innerHTML = html;
    
    document.querySelectorAll('.btn-eliminar-pregunta').forEach(btn => {
        btn.addEventListener('click', function() {
            const index = parseInt(this.dataset.index);
            eliminarPreguntaManual(index);
        });
    });
    
    const panelManual = document.getElementById('panelManual');
    const panelManualDetalle = document.getElementById('panelManualDetalle');
    if (panelManual) panelManual.style.display = 'none';
    if (panelManualDetalle) panelManualDetalle.style.display = 'block';
}

function eliminarPreguntaManual(index) {
    const preguntaItem = document.querySelector(`.pregunta-item-manual[data-index="${index}"]`);
    if (preguntaItem) {
        preguntaItem.remove();
        const items = document.querySelectorAll('.pregunta-item-manual');
        items.forEach((item, newIndex) => {
            item.dataset.index = newIndex;
            const header = item.querySelector('.pregunta-header-manual h4');
            if (header) header.textContent = `Pregunta ${newIndex + 1}`;
            const eliminarBtn = item.querySelector('.btn-eliminar-pregunta');
            if (eliminarBtn) eliminarBtn.dataset.index = newIndex;
        });
    }
}

function guardarPreguntasManuales() {
    const preguntas = [];
    const items = document.querySelectorAll('.pregunta-item-manual');
    let tieneError = false;
    
    items.forEach((item, idx) => {
        const enunciado = item.querySelector('.pregunta-enunciado-input')?.value.trim() || '';
        const retroalimentacion = item.querySelector('.retroalimentacion-input')?.value.trim() || '';
        
        if (!enunciado) {
            mostrarNotificacion(`La pregunta ${idx + 1} no tiene enunciado`, 'error');
            tieneError = true;
            return;
        }
        
        const radios = item.querySelectorAll('input[type="radio"]');
        let correcta = '';
        let opciones = [];
        
        radios.forEach(radio => {
            if (radio.checked) correcta = radio.value;
        });
        
        const opcionesInputs = item.querySelectorAll('.opcion-texto-input');
        opcionesInputs.forEach(input => {
            if (input.value.trim()) opciones.push(input.value.trim());
        });
        
        const tipo = document.getElementById('tipoManual').value;
        
        if (tipo === 'opcion_multiple' && opciones.length < 2) {
            mostrarNotificacion(`La pregunta ${idx + 1} debe tener al menos 2 opciones`, 'error');
            tieneError = true;
            return;
        }
        
        if (!correcta) {
            mostrarNotificacion(`La pregunta ${idx + 1} no tiene respuesta correcta seleccionada`, 'error');
            tieneError = true;
            return;
        }
        
        const nivel = document.getElementById('nivelManual').value;
        const asignatura = document.getElementById('asignaturaManual').value;
        const dimension = document.getElementById('dimensionManual').value;
        const bloom = 'comprender';
        const dificultad = 'media';
        
        preguntas.push({
            enunciado: enunciado,
            tipo: tipo,
            opciones: opciones,
            respuesta_correcta: correcta,
            retroalimentacion: retroalimentacion,
            nivel: nivel,
            asignatura: asignatura,
            dimension: dimension,
            bloom: bloom,
            dificultad: dificultad,
            tema: document.getElementById('temaManual').value,
            tiempo: parseInt(document.getElementById('tiempoManual').value) || 30,
            estado: 'pendiente'
        });
    });
    
    if (tieneError || preguntas.length === 0) return;
    
    agregarPreguntasATabla(preguntas);
    cerrarModal();
}

function generarPreguntasIA() {
    const estadoGenerador = document.getElementById('estadoGeneradorIA');
    const contenedorPreguntas = document.getElementById('contenedorPreguntasIA');
    const acciones = document.getElementById('accionesPreguntasIA');
    
    if (estadoGenerador) {
        estadoGenerador.innerHTML = `
            <div class="estado-icono-ia loading">
                <i class="fas fa-spinner fa-pulse"></i>
            </div>
            <div class="estado-contenido-ia">
                <h3>Generando preguntas...</h3>
                <p>La IA está creando preguntas basadas en tus parámetros.</p>
            </div>
        `;
    }
    
    const tiposSeleccionados = Array.from(document.querySelectorAll('#formGeneradorIA input[type="checkbox"]:checked')).map(cb => cb.value);
    
    if (tiposSeleccionados.length === 0) {
        mostrarNotificacion('Selecciona al menos un tipo de pregunta', 'error');
        if (estadoGenerador) {
            estadoGenerador.innerHTML = `
                <div class="estado-icono-ia">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="estado-contenido-ia">
                    <h3>Error</h3>
                    <p>Selecciona al menos un tipo de pregunta para generar</p>
                </div>
            `;
        }
        return;
    }
    
    const params = {
        cantidad: parseInt(document.getElementById('cantidadIA').value) || 5,
        nivel: document.getElementById('nivelIA').value,
        asignatura: document.getElementById('asignaturaIA').value,
        dimension: document.getElementById('dimensionIA').value,
        tipos: tiposSeleccionados,
        bloom: document.getElementById('bloomIA').value,
        instrucciones: document.getElementById('instruccionesIA').value
    };
    
    if (!params.nivel || !params.asignatura) {
        mostrarNotificacion('Selecciona nivel y asignatura', 'error');
        return;
    }
    
    setTimeout(() => {
        generatedQuestions = [];
        for (let i = 0; i < params.cantidad; i++) {
            const tipo = params.tipos[i % params.tipos.length];
            const temas = [
                `los principios fundamentales de ${params.asignatura}`,
                `las características de la ${params.dimension} en educación`,
                `los conceptos clave del nivel ${params.nivel}`,
                `las estrategias didácticas para ${params.asignatura}`
            ];
            
            let enunciado, opciones, respuestaCorrecta;
            
            if (tipo === 'opcion_multiple') {
                enunciado = `¿Cuál de las siguientes opciones describe correctamente ${temas[i % temas.length]} según la Nueva Escuela Mexicana?`;
                opciones = [
                    "Enfoque centrado en la comunidad",
                    "Desarrollo de habilidades socioemocionales",
                    "Aprendizaje basado en proyectos",
                    "Evaluación formativa continua"
                ];
                respuestaCorrecta = Math.floor(Math.random() * 4).toString();
            } else {
                const afirmaciones = [
                    `La ${params.dimension} es fundamental para el desarrollo docente en ${params.nivel}.`,
                    `Los estudiantes de ${params.nivel} requieren enfoques específicos en ${params.asignatura}.`,
                    `La evaluación formativa es un componente esencial de la ${params.dimension} educativa.`,
                    `El trabajo colaborativo favorece el aprendizaje significativo en ${params.asignatura}.`
                ];
                enunciado = `${afirmaciones[i % afirmaciones.length]} ¿Esta afirmación es verdadera o falsa?`;
                opciones = ["Verdadero", "Falso"];
                respuestaCorrecta = i % 2 === 0 ? "true" : "false";
            }
            
            generatedQuestions.push({
                enunciado: enunciado,
                tipo: tipo,
                opciones: opciones,
                respuesta_correcta: respuestaCorrecta,
                retroalimentacion: `Según los lineamientos de ${params.asignatura} para ${params.nivel}, esta respuesta es correcta.`,
                nivel: params.nivel,
                asignatura: params.asignatura,
                dimension: params.dimension,
                bloom: params.bloom,
                dificultad: i % 2 === 0 ? 'media' : 'baja',
                estado: 'pendiente'
            });
        }
        
        mostrarPreguntasIAGeneradas(generatedQuestions);
        
        if (estadoGenerador) estadoGenerador.style.display = 'none';
        if (contenedorPreguntas) contenedorPreguntas.style.display = 'block';
        if (acciones) acciones.style.display = 'flex';
        
        const contador = document.getElementById('contadorPreguntasIA');
        if (contador) contador.textContent = generatedQuestions.length;
        
        mostrarNotificacion(`${generatedQuestions.length} preguntas generadas`, 'success');
    }, 1500);
}

function mostrarPreguntasIAGeneradas(preguntas) {
    const container = document.getElementById('contenedorPreguntasIA');
    if (!container) return;
    
    let html = '<div class="preguntas-lista-ia">';
    
    preguntas.forEach((pregunta, idx) => {
        const tipoTexto = pregunta.tipo === 'opcion_multiple' ? 'Opción Múltiple' : 'Verdadero/Falso';
        html += `
            <div class="pregunta-generada-item" data-idx="${idx}">
                <div class="pregunta-generada-header">
                    <div class="pregunta-titulo">
                        <span class="pregunta-numero">Pregunta ${idx + 1}</span>
                        <span class="pregunta-tipo-badge ${pregunta.tipo}">${tipoTexto}</span>
                    </div>
                    <div class="pregunta-acciones">
                        <button class="btn-icon btn-sm btn-editar-pregunta-ia" title="Editar" data-idx="${idx}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon btn-sm btn-eliminar-pregunta-ia" title="Eliminar" data-idx="${idx}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="pregunta-generada-enunciado">
                    <strong>Enunciado:</strong> ${escapeHtml(pregunta.enunciado)}
                </div>
                <div class="pregunta-generada-opciones">
                    <strong>Opciones:</strong>
                    <ul>
        `;
        
        pregunta.opciones.forEach((opcion, optIdx) => {
            let isCorrect = false;
            if (pregunta.tipo === 'opcion_multiple') {
                isCorrect = parseInt(pregunta.respuesta_correcta) === optIdx;
            } else {
                isCorrect = (pregunta.respuesta_correcta === 'true' && optIdx === 0) ||
                           (pregunta.respuesta_correcta === 'false' && optIdx === 1);
            }
            html += `<li class="${isCorrect ? 'opcion-correcta' : ''}">
                        ${escapeHtml(opcion)} ${isCorrect ? '<i class="fas fa-check-circle correct-icon"></i>' : ''}
                    </li>`;
        });
        
        html += `
                    </ul>
                </div>
                <div class="pregunta-generada-meta">
                    <span class="meta-badge"><i class="fas fa-graduation-cap"></i> ${getNivelTexto(pregunta.nivel)}</span>
                    <span class="meta-badge"><i class="fas fa-book"></i> ${getAsignaturaTexto(pregunta.asignatura)}</span>
                    <span class="meta-badge"><i class="fas fa-layer-group"></i> ${getDimensionTexto(pregunta.dimension)}</span>
                    <span class="meta-badge"><i class="fas fa-brain"></i> ${getBloomTexto(pregunta.bloom)}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    document.querySelectorAll('.btn-editar-pregunta-ia').forEach(btn => {
        btn.addEventListener('click', function() {
            const idx = parseInt(this.dataset.idx);
            const nuevoEnunciado = prompt('Editar enunciado:', generatedQuestions[idx].enunciado);
            if (nuevoEnunciado && nuevoEnunciado.trim()) {
                generatedQuestions[idx].enunciado = nuevoEnunciado.trim();
                mostrarPreguntasIAGeneradas(generatedQuestions);
                mostrarNotificacion('Pregunta editada', 'success');
            }
        });
    });
    
    document.querySelectorAll('.btn-eliminar-pregunta-ia').forEach(btn => {
        btn.addEventListener('click', function() {
            const idx = parseInt(this.dataset.idx);
            if (confirm('¿Eliminar esta pregunta?')) {
                generatedQuestions.splice(idx, 1);
                if (generatedQuestions.length === 0) {
                    const estadoGenerador = document.getElementById('estadoGeneradorIA');
                    const contenedorPreguntas = document.getElementById('contenedorPreguntasIA');
                    const acciones = document.getElementById('accionesPreguntasIA');
                    if (estadoGenerador) estadoGenerador.style.display = 'flex';
                    if (contenedorPreguntas) contenedorPreguntas.style.display = 'none';
                    if (acciones) acciones.style.display = 'none';
                } else {
                    mostrarPreguntasIAGeneradas(generatedQuestions);
                }
                const contador = document.getElementById('contadorPreguntasIA');
                if (contador) contador.textContent = generatedQuestions.length;
                mostrarNotificacion('Pregunta eliminada', 'info');
            }
        });
    });
}

function enviarPreguntasIAValidacion() {
    if (generatedQuestions.length === 0) {
        mostrarNotificacion('No hay preguntas para enviar', 'error');
        return;
    }
    
    agregarPreguntasATabla(generatedQuestions);
    cerrarModal();
}

function descargarPreguntasIA() {
    if (generatedQuestions.length === 0) {
        mostrarNotificacion('No hay preguntas para descargar', 'error');
        return;
    }
    
    const dataStr = JSON.stringify(generatedQuestions, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', `preguntas_ia_${new Date().toISOString().slice(0,19)}.json`);
    linkElement.click();
    
    mostrarNotificacion('Preguntas descargadas', 'success');
}

function desecharPreguntasIA() {
    if (confirm('¿Desechar todas las preguntas generadas?')) {
        generatedQuestions = [];
        const estadoGenerador = document.getElementById('estadoGeneradorIA');
        const contenedorPreguntas = document.getElementById('contenedorPreguntasIA');
        const acciones = document.getElementById('accionesPreguntasIA');
        
        if (estadoGenerador) {
            estadoGenerador.style.display = 'flex';
            estadoGenerador.innerHTML = `
                <div class="estado-icono-ia"><i class="fas fa-robot"></i></div>
                <div class="estado-contenido-ia">
                    <h3>Listo para generar</h3>
                    <p>Configura los parámetros y haz clic en "Generar Preguntas con IA"</p>
                </div>
            `;
        }
        if (contenedorPreguntas) contenedorPreguntas.style.display = 'none';
        if (acciones) acciones.style.display = 'none';
        
        mostrarNotificacion('Todas las preguntas han sido desechadas', 'info');
    }
}

function limpiarFormularioIA() {
    document.getElementById('cantidadIA').value = 5;
    document.getElementById('nivelIA').value = 'primaria';
    document.getElementById('asignaturaIA').value = 'matematicas';
    document.getElementById('dimensionIA').value = 'pedagogica';
    document.getElementById('bloomIA').value = 'comprender';
    document.getElementById('instruccionesIA').value = '';
    
    const tipoCheckboxes = document.querySelectorAll('#formGeneradorIA input[type="checkbox"]');
    tipoCheckboxes.forEach(cb => cb.checked = cb.value === 'opcion_multiple');
    
    mostrarNotificacion('Formulario limpiado', 'info');
}

// ==================== FUNCIONES AUXILIARES ====================

function getTipoTexto(tipo) {
    const tipos = { 'opcion_multiple': 'Opción Múltiple', 'verdadero_falso': 'Verdadero/Falso',
        'caso_practico': 'Caso Práctico', 'relacionar': 'Relacionar', 'completar': 'Completar' };
    return tipos[tipo] || tipo;
}

function getNivelTexto(nivel) {
    const niveles = { 'preescolar': 'Preescolar', 'primaria': 'Primaria', 'secundaria': 'Secundaria', 'media_superior': 'Media Superior' };
    return niveles[nivel] || nivel;
}

function getAsignaturaTexto(asignatura) {
    const asignaturas = { 'espanol': 'Español', 'matematicas': 'Matemáticas', 'ciencias': 'Ciencias Naturales',
        'historia': 'Historia', 'geografia': 'Geografía', 'formacion_civica': 'Formación Cívica',
        'artes': 'Artes', 'educacion_fisica': 'Educación Física', 'ingles': 'Inglés',
        'pedagogia': 'Pedagogía', 'evaluacion': 'Evaluación', 'inclusion': 'Inclusión' };
    return asignaturas[asignatura] || asignatura;
}

function getDimensionTexto(dimension) {
    const dimensiones = { 'pedagogica': 'Pedagógica', 'disciplinar': 'Disciplinar', 'didactica': 'Didáctica',
        'gestion': 'Gestión Escolar', 'tic': 'Tecnologías (TIC)', 'vinculacion': 'Vinculación', 'inclusion': 'Inclusión' };
    return dimensiones[dimension] || dimension;
}

function getBloomTexto(bloom) {
    const niveles = { 'recordar': 'Recordar', 'comprender': 'Comprender', 'aplicar': 'Aplicar',
        'analizar': 'Analizar', 'evaluar': 'Evaluar', 'crear': 'Crear' };
    return niveles[bloom] || bloom;
}

function getDificultadTexto(dificultad) {
    const dificultades = { 'baja': 'Baja', 'media': 'Media', 'alta': 'Alta' };
    return dificultades[dificultad] || dificultad;
}

function getEstadoTexto(estado) {
    const estados = { 'validada': 'Validada', 'pendiente': 'Pendiente', 'archivada': 'Archivada', 'rechazada': 'Rechazada' };
    return estados[estado] || estado;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function mostrarNotificacion(mensaje, tipo = 'info') {
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
    }, 4000);
}

// Exportar funciones necesarias
window.agregarPreguntasATabla = agregarPreguntasATabla;