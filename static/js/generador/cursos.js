// ==================== CURSOS.JS - Generador de Cursos ====================
// Módulo para gestionar cursos mediante AJAX

// Variables globales
let cursosGlobales = [];
let cursoActual = null;

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', function() {
    cargarCursosUsuario();
    inicializarEventosCursos();
});

// ==================== FUNCIONES DE CARGA ====================

function cargarCursosUsuario() {
    fetch('/generador/ajax/datos/')
        .then(response => response.json())
        .then(data => {
            if (data.cursos_bd) {
                cursosGlobales = data.cursos_bd;
                renderizarCursos();
            }
        })
        .catch(error => {
            console.error('Error al cargar cursos:', error);
            // Fallback a localStorage
            const storedCursos = localStorage.getItem('generador_cursos');
            if (storedCursos) {
                cursosGlobales = JSON.parse(storedCursos);
                renderizarCursos();
            }
        });
}

// ==================== RENDERIZADO ====================

function renderizarCursos() {
    const container = document.querySelector('.cursos-grid') || document.querySelector('.course-list');
    if (!container) return;
    
    if (cursosGlobales.length === 0) {
        container.innerHTML = `
            <div class="sin-cursos" style="grid-column: 1/-1; text-align: center; padding: 60px;">
                <i class="fas fa-folder-open" style="font-size: 64px; color: #cbd5e1; margin-bottom: 16px;"></i>
                <p style="color: #64748b;">No tienes cursos creados aún</p>
                <button class="btn btn-primary" onclick="window.location.href='/generador/generador_de_cursos/'">
                    <i class="fas fa-plus-circle"></i> Crear primer curso
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = cursosGlobales.map(curso => renderizarTarjetaCurso(curso)).join('');
    
    // Agregar eventos a las tarjetas
    document.querySelectorAll('.btn-editar-curso').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            editarCurso(id);
        });
    });
    
    document.querySelectorAll('.btn-eliminar-curso').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            eliminarCurso(id);
        });
    });
}

function renderizarTarjetaCurso(curso) {
    const estadoClass = obtenerEstadoClass(curso.estado);
    const estadoIcon = obtenerEstadoIcon(curso.estado);
    
    return `
        <div class="course-card" data-curso-id="${curso.id_curso}" onclick="verDetalleCurso(${curso.id_curso})">
            <div class="course-header">
                <h3>${curso.titulo}</h3>
                <span class="course-status ${estadoClass}">
                    <i class="${estadoIcon}"></i> ${curso.estado}
                </span>
            </div>
            <p class="course-description">${curso.descripcion || 'Sin descripción'}</p>
            <div class="course-meta">
                <span><i class="fas fa-calendar"></i> ${formatearFecha(curso.fecha_creacion)}</span>
                <span><i class="fas fa-robot"></i> ${curso.generado_con_ia ? 'IA' : 'Manual'}</span>
            </div>
            <div class="course-actions">
                <button class="btn btn-sm btn-outline btn-editar-curso" data-id="${curso.id_curso}">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="btn btn-sm btn-danger btn-eliminar-curso" data-id="${curso.id_curso}">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        </div>
    `;
}

// ==================== OPERACIONES CRUD ====================

function crearCurso(datos) {
    return fetch('/generador/api/crear-curso-generador/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'Curso creado',
                text: data.mensaje,
                timer: 1500,
                showConfirmButton: false
            });
            cargarCursosUsuario(); // Recargar lista
            return data;
        } else {
            throw new Error(data.error || 'Error al crear curso');
        }
    });
}

function editarCurso(cursoId) {
    const curso = cursosGlobales.find(c => c.id_curso === cursoId);
    if (!curso) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Curso no encontrado'
        });
        return;
    }
    
    // Redirigir al editor con el ID del curso
    window.location.href = `/generador/generador_de_cursos/?curso_id=${cursoId}`;
}

function actualizarCurso(cursoId, datos) {
    return fetch(`/generador/api/actualizar-curso-generador/${cursoId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'Curso actualizado',
                text: data.mensaje,
                timer: 1500,
                showConfirmButton: false
            });
            cargarCursosUsuario(); // Recargar lista
            return data;
        } else {
            throw new Error(data.error || 'Error al actualizar curso');
        }
    });
}

function eliminarCurso(cursoId) {
    const curso = cursosGlobales.find(c => c.id_curso === cursoId);
    if (!curso) return;
    
    Swal.fire({
        title: '¿Eliminar curso?',
        text: `¿Estás seguro de eliminar "${curso.titulo}"? Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#691C32',
        cancelButtonColor: '#64748B',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/generador/api/eliminar-curso-generador/${cursoId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Eliminado',
                        text: data.mensaje,
                        timer: 1500,
                        showConfirmButton: false
                    });
                    cargarCursosUsuario(); // Recargar lista
                } else {
                    throw new Error(data.error || 'Error al eliminar curso');
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: error.message
                });
            });
        }
    });
}

function verDetalleCurso(cursoId) {
    const curso = cursosGlobales.find(c => c.id_curso === cursoId);
    if (!curso) return;
    
    // Redirigir a la vista de detalle
    window.location.href = `/generador/generador_de_cursos/?curso_id=${cursoId}`;
}

// ==================== FUNCIONES AUXILIARES ====================

function obtenerEstadoClass(estado) {
    const estados = {
        'Borrador': 'status-draft',
        'Aprobado': 'status-approved',
        'Rechazado': 'status-rejected',
        'En_Revisión': 'status-review',
        'Publicado': 'status-published'
    };
    return estados[estado] || 'status-draft';
}

function obtenerEstadoIcon(estado) {
    const iconos = {
        'Borrador': 'fas fa-file-alt',
        'Aprobado': 'fas fa-check-circle',
        'Rechazado': 'fas fa-times-circle',
        'En_Revisión': 'fas fa-clock',
        'Publicado': 'fas fa-globe'
    };
    return iconos[estado] || 'fas fa-file-alt';
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return 'N/A';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function inicializarEventosCursos() {
    // Eventos específicos del generador de cursos
    const btnCrearCurso = document.getElementById('btnCrearCurso');
    if (btnCrearCurso) {
        btnCrearCurso.addEventListener('click', () => {
            window.location.href = '/generador/generador_de_cursos/';
        });
    }
}