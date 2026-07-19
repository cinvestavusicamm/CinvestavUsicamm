// ========================
// DATOS DEL CALENDARIO
// ========================
const eventosData = [
    // Evaluaciones
    { title: 'Evaluación Primaria', start: '2024-06-10T09:00:00', end: '2024-06-10T12:00:00', className: 'evento-evaluacion-fc', tipo: 'evaluacion', descripcion: 'Evaluación para promoción horizontal de maestros de primaria', lugar: 'Plataforma en línea' },
    { title: 'Evaluación Secundaria', start: '2024-06-15T09:00:00', end: '2024-06-15T12:00:00', className: 'evento-evaluacion-fc', tipo: 'evaluacion', descripcion: 'Evaluación para promoción horizontal de maestros de secundaria', lugar: 'Plataforma en línea' },
    // Plazos
    { title: 'Plazo: Revisión preguntas', start: '2024-06-04', allDay: true, className: 'evento-plazo-fc', tipo: 'plazo', descripcion: 'Fecha límite para revisar preguntas generadas por IA', lugar: 'Sistema USICAMM' },
    { title: 'Plazo límite validación IA', start: '2024-06-18', allDay: true, className: 'evento-plazo-fc', tipo: 'plazo', descripcion: 'Fecha límite para validar preguntas generadas por IA', lugar: 'Sistema USICAMM' },
    // Revisiones
    { title: 'Revisión colegas', start: '2024-06-20T16:00:00', end: '2024-06-20T18:00:00', className: 'evento-revision-fc', tipo: 'revision', descripcion: 'Revisión conjunta con colegas evaluadores', lugar: 'Sala 3, USICAMM' },
    // Publicaciones
    { title: 'Publicación resultados', start: '2024-06-13T10:00:00', className: 'evento-publicacion-fc', tipo: 'publicacion', descripcion: 'Publicación de resultados primera etapa', lugar: 'Portal USICAMM' },
    { title: 'Convocatoria 2027', start: '2024-06-28T09:00:00', className: 'evento-convocatoria-fc', tipo: 'convocatoria', descripcion: 'Publicación oficial convocatoria 2027', lugar: 'Portal oficial' },
    // Reuniones
    { title: 'Reunión USICAMM', start: '2024-06-06T11:00:00', end: '2024-06-06T13:00:00', className: 'evento-reunion-fc', tipo: 'reunion', descripcion: 'Reunión general del equipo USICAMM', lugar: 'Auditorio principal' },
    { title: 'Capacitación NEM', start: '2024-06-26T09:00:00', end: '2024-06-26T14:00:00', className: 'evento-capacitacion-fc', tipo: 'capacitacion', descripcion: 'Capacitación sobre Nuevo Modelo Educativo', lugar: 'Centro de capacitación' }
];

const procesosData = [
    { proceso: 'Promoción Horizontal 2026', tipo: 'evaluacion', fechaInicio: '04/03/2024', fechaFin: '30/03/2024', estado: 'en-curso', descripcion: 'Evaluación de conocimientos y aptitudes' },
    { proceso: 'Promoción Vertical 2026', tipo: 'evaluacion', fechaInicio: '15/06/2024', fechaFin: '15/11/2024', estado: 'en-curso', descripcion: 'Ascenso a cargos directivos' },
    { proceso: 'Validación Preguntas IA', tipo: 'revision', fechaInicio: '01/06/2024', fechaFin: '18/06/2024', estado: 'critico', descripcion: 'Revisión de contenido generado' },
    { proceso: 'Publicación Resultados', tipo: 'publicacion', fechaInicio: '13/06/2024', fechaFin: '13/06/2024', estado: 'proximo', descripcion: 'Primera etapa horizontal' },
    { proceso: 'Capacitación NEM 2024', tipo: 'capacitacion', fechaInicio: '26/06/2024', fechaFin: '26/06/2024', estado: 'proximo', descripcion: 'Formación para evaluadores' },
    { proceso: 'Convocatoria 2027', tipo: 'convocatoria', fechaInicio: '28/06/2024', fechaFin: '28/06/2024', estado: 'proximo', descripcion: 'Publicación oficial' }
];

let calendar;

// ========================
// FUNCIONES AUXILIARES
// ========================
function formatearFecha(fechaStr) {
    const partes = fechaStr.split('/');
    return `${partes[2]}-${partes[1]}-${partes[0]}`;
}

function calcularDiasRestantes(fechaFinStr) {
    const hoy = new Date();
    const partes = fechaFinStr.split('/');
    const fechaFin = new Date(partes[2], partes[1] - 1, partes[0]);
    return Math.ceil((fechaFin - hoy) / (1000 * 60 * 60 * 24));
}

function getEstadoBadge(estado) {
    const badges = {
        'en-curso': '<span class="badge badge-en-curso">En curso</span>',
        'proximo': '<span class="badge badge-proximo">Próximo</span>',
        'critico': '<span class="badge badge-critico">Crítico</span>'
    };
    return badges[estado] || '<span class="badge">' + estado + '</span>';
}

// ========================
// RENDERIZAR PRÓXIMOS EVENTOS
// ========================
function renderizarProximosEventos() {
    const container = document.getElementById('listaProximosEventos');
    if (!container) return;
    
    const hoy = new Date();
    const meses = { 1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC' };
    const tipos = { 'evaluacion': 'Evaluación', 'plazo': 'Plazo', 'revision': 'Revisión', 'publicacion': 'Publicación', 'reunion': 'Reunión', 'capacitacion': 'Capacitación', 'convocatoria': 'Convocatoria' };
    
    const proximos = eventosData
        .filter(e => new Date(e.start) >= hoy)
        .sort((a, b) => new Date(a.start) - new Date(b.start))
        .slice(0, 5);
    
    container.innerHTML = proximos.map(e => {
        const fecha = new Date(e.start);
        return `
            <div class="evento-proximo" data-fecha="${e.start.split('T')[0]}">
                <div class="evento-fecha">
                    <div class="evento-dia">${fecha.getDate()}</div>
                    <div class="evento-mes">${meses[fecha.getMonth() + 1]}</div>
                </div>
                <div class="evento-contenido">
                    <h3>${e.title}</h3>
                    <p>${e.descripcion}</p>
                    <div class="evento-meta">
                        <span><i class="fas fa-clock"></i> ${e.start.includes('T') ? e.start.split('T')[1].slice(0,5) : 'Todo el día'}</span>
                        <span><i class="fas fa-map-marker-alt"></i> ${e.lugar}</span>
                    </div>
                </div>
                <div class="evento-badge evento-${e.tipo}">${tipos[e.tipo] || e.tipo}</div>
            </div>
        `;
    }).join('');
    
    document.querySelectorAll('.evento-proximo').forEach(el => {
        el.addEventListener('click', function() {
            const fecha = this.dataset.fecha;
            if (fecha && calendar) calendar.gotoDate(fecha);
        });
    });
}

// ========================
// RENDERIZAR TABLA DE PROCESOS
// ========================
function renderizarTablaProcesos(filtroTipo = '', filtroFecha = '') {
    const tbody = document.getElementById('tablaProcesosBody');
    if (!tbody) return;
    
    let filtrados = [...procesosData];
    if (filtroTipo) filtrados = filtrados.filter(p => p.tipo === filtroTipo);
    if (filtroFecha) filtrados = filtrados.filter(p => p.fechaInicio === filtroFecha || p.fechaFin === filtroFecha);
    
    tbody.innerHTML = filtrados.map(p => {
        const dias = calcularDiasRestantes(p.fechaFin);
        const tipos = { 'evaluacion': 'Evaluación', 'plazo': 'Plazo', 'revision': 'Revisión', 'publicacion': 'Publicación', 'capacitacion': 'Capacitación', 'convocatoria': 'Convocatoria' };
        return `
            <tr data-fecha="${formatearFecha(p.fechaInicio)}">
                <td><strong>${p.proceso}</strong><br><small>${p.descripcion}</small></td>
                <td>${tipos[p.tipo] || p.tipo}</td>
                <td>${p.fechaInicio}</td>
                <td>${p.fechaFin}</td>
                <td>${getEstadoBadge(p.estado)}</td>
                <td><div class="tiempo-restante ${dias <= 7 ? 'critico' : ''}"><i class="fas ${dias <= 7 ? 'fa-exclamation-triangle' : 'fa-hourglass-half'}"></i> ${dias} días</div></td>
            </tr>
        `;
    }).join('');
    
    document.querySelectorAll('#tablaProcesosBody tr').forEach(row => {
        row.addEventListener('click', function() {
            const fecha = this.dataset.fecha;
            if (fecha && calendar) calendar.gotoDate(fecha);
        });
    });
}

// ========================
// MODAL NUEVO EVENTO
// ========================
const modal = document.getElementById('modalNuevoEvento');
const btnNuevoEvento = document.getElementById('btnNuevoEvento');
const btnCerrarModal = document.getElementById('btnCerrarModal');
const btnCancelarEvento = document.getElementById('btnCancelarEvento');
const btnGuardarEvento = document.getElementById('btnGuardarEvento');

function seleccionarColor(color) {
    document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
    const selected = document.querySelector(`.color-option[data-color="${color}"]`);
    if (selected) {
        selected.classList.add('selected');
        document.getElementById('eventoColor').value = color;
    }
}

function abrirModal() {
    document.getElementById('eventoFecha').value = new Date().toISOString().split('T')[0];
    seleccionarColor('evaluacion');
    modal.classList.add('active');
}

function cerrarModal() {
    modal.classList.remove('active');
    document.getElementById('formNuevoEvento').reset();
    seleccionarColor('evaluacion');
}

if (btnNuevoEvento) btnNuevoEvento.addEventListener('click', abrirModal);
if (btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModal);
if (btnCancelarEvento) btnCancelarEvento.addEventListener('click', cerrarModal);
modal?.addEventListener('click', e => { if (e.target === modal) cerrarModal(); });

document.querySelectorAll('.color-option').forEach(opt => {
    opt.addEventListener('click', () => seleccionarColor(opt.dataset.color));
});

document.getElementById('eventoTipo')?.addEventListener('change', function() {
    if (this.value) seleccionarColor(this.value);
});

if (btnGuardarEvento) {
    btnGuardarEvento.addEventListener('click', () => {
        const form = document.getElementById('formNuevoEvento');
        if (!form.checkValidity()) return alert('Completa los campos requeridos');
        
        const titulo = document.getElementById('eventoTitulo').value;
        const fecha = document.getElementById('eventoFecha').value;
        const horaInicio = document.getElementById('eventoHoraInicio').value;
        const horaFin = document.getElementById('eventoHoraFin').value;
        const tipo = document.getElementById('eventoTipo').value;
        const color = document.getElementById('eventoColor').value;
        const lugar = document.getElementById('eventoUbicacion').value || 'Por definir';
        const descripcion = document.getElementById('eventoDescripcion').value || 'Sin descripción';
        
        calendar.addEvent({
            title: titulo,
            start: horaInicio ? `${fecha}T${horaInicio}` : fecha,
            end: horaFin ? `${fecha}T${horaFin}` : fecha,
            allDay: !horaInicio,
            className: `evento-${color}-fc`,
            extendedProps: { tipo, descripcion, lugar }
        });
        
        cerrarModal();
        alert(`Evento "${titulo}" agregado`);
        calendar.gotoDate(fecha);
    });
}

// ========================
// INICIALIZAR CALENDARIO
// ========================
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        headerToolbar: false,
        height: '100%',
        dayMaxEvents: 3,
        events: eventosData.map(e => ({
            ...e,
            extendedProps: { tipo: e.tipo, descripcion: e.descripcion, lugar: e.lugar }
        })),
        eventClick: function(info) {
            const e = info.event;
            const tipos = { evaluacion: 'Evaluación', plazo: 'Plazo', revision: 'Revisión', publicacion: 'Publicación', reunion: 'Reunión', capacitacion: 'Capacitación', convocatoria: 'Convocatoria' };
            alert(`${e.title}\n\nTipo: ${tipos[e.extendedProps.tipo]}\nFecha: ${e.start.toLocaleDateString()}\nLugar: ${e.extendedProps.lugar}\n\n${e.extendedProps.descripcion}`);
        },
        datesSet: function(info) {
            const fecha = info.view.currentStart;
            document.getElementById('mesActual').textContent = fecha.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase());
        }
    });
    
    calendar.render();
    
    // Controles
    document.getElementById('btnAnteriorMes')?.addEventListener('click', () => calendar.prev());
    document.getElementById('btnSiguienteMes')?.addEventListener('click', () => calendar.next());
    document.getElementById('btnHoy')?.addEventListener('click', () => calendar.today());
    document.getElementById('btnVerTodosEventos')?.addEventListener('click', () => calendar.changeView('listMonth'));
    
    // Filtros
    const filtroTipo = document.getElementById('filtroTipo');
    const filtroFecha = document.getElementById('filtroFecha');
    const aplicarFiltros = () => {
        const tipo = filtroTipo?.value || '';
        const fecha = filtroFecha?.value || '';
        calendar.getEvents().forEach(e => {
            const matchTipo = !tipo || e.extendedProps?.tipo === tipo;
            const matchFecha = !fecha || e.start.toISOString().split('T')[0] === fecha;
            e.setProp('display', matchTipo && matchFecha ? 'auto' : 'none');
        });
        renderizarTablaProcesos(tipo, fecha);
    };
    
    document.getElementById('btnAplicarFiltro')?.addEventListener('click', aplicarFiltros);
    document.getElementById('btnLimpiarFiltro')?.addEventListener('click', () => {
        if (filtroTipo) filtroTipo.value = '';
        if (filtroFecha) filtroFecha.value = '';
        calendar.getEvents().forEach(e => e.setProp('display', 'auto'));
        renderizarTablaProcesos();
    });
    
    if (filtroFecha) filtroFecha.value = new Date().toISOString().split('T')[0];
    
    renderizarProximosEventos();
    renderizarTablaProcesos();
});