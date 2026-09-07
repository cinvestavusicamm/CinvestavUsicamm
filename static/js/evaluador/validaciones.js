// ===== VALIDACIONES: NAVEGACIÓN Y ACCIONES SOBRE PREGUNTAS PENDIENTES =====

document.addEventListener('DOMContentLoaded', function () {
    // Variables de estado
    let preguntaActual = 1;
    const totalPreguntas = Number(document.body.dataset.totalPendientes || 0);
    const pendientes = document.querySelectorAll('.pendiente-item');

    // Actualizar contadores
    function actualizarContadores() {
        document.getElementById('numeroActual').textContent = preguntaActual;
        document.getElementById('totalPendientes').textContent = totalPreguntas;
        document.getElementById('contadorPendientes').textContent = totalPreguntas;
    }

    // Inicializar contadores
    actualizarContadores();

    // Navegación entre preguntas
    document.getElementById('btnAnterior')?.addEventListener('click', function () {
        if (preguntaActual > 1) {
            preguntaActual--;
            actualizarContadores();
            actualizarPreguntaActiva();
            console.log('Pregunta anterior:', preguntaActual);
        }
    });

    document.getElementById('btnSiguiente')?.addEventListener('click', function () {
        if (preguntaActual < totalPreguntas) {
            preguntaActual++;
            actualizarContadores();
            actualizarPreguntaActiva();
            console.log('Pregunta siguiente:', preguntaActual);
        }
    });

    // Actualizar pregunta activa en la lista
    function actualizarPreguntaActiva() {
        pendientes.forEach(item => {
            item.classList.remove('activa');
            const itemId = parseInt(item.getAttribute('data-id'));
            if (itemId === preguntaActual) {
                item.classList.add('activa');
            }
        });
    }

    // Hacer clic en items de la lista
    pendientes.forEach(item => {
        item.addEventListener('click', function () {
            const itemId = parseInt(this.getAttribute('data-id'));
            preguntaActual = itemId;
            actualizarContadores();
            actualizarPreguntaActiva();

            // Simular cambio de pregunta (en realidad cambiaría el contenido)
            console.log('Cargando pregunta:', itemId);
        });
    });

    // Acciones de validación
    document.getElementById('btnAprobar')?.addEventListener('click', async function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        
        try {
            const response = await fetch(`/evaluador/api/aprobar-pregunta/${preguntaActual}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    curso_id: obtenerCursoIdActual(),
                    comentarios: comentarios,
                    iteracion: '1',
                    fecha_revision: new Date().toISOString(),
                    actualizar_curso: true
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Aprobada',
                    text: `Pregunta #${preguntaActual} aprobada correctamente.`,
                    timer: 1500,
                    showConfirmButton: false
                });
                siguientePregunta();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Error al aprobar la pregunta'
                });
            }
        } catch (error) {
            console.error('Error al aprobar:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error de conexión al aprobar la pregunta'
            });
        }
    });

    document.getElementById('btnRechazar')?.addEventListener('click', async function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        if (!comentarios.trim()) {
            Swal.fire({
                icon: 'warning',
                title: 'Comentarios requeridos',
                text: 'Por favor, ingresa los motivos del rechazo en los comentarios.'
            });
            return;
        }

        try {
            const response = await fetch(`/evaluador/api/rechazar-pregunta/${preguntaActual}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    curso_id: obtenerCursoIdActual(),
                    comentarios: comentarios,
                    iteracion: '1',
                    fecha_revision: new Date().toISOString()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Rechazada',
                    text: `Pregunta #${preguntaActual} rechazada correctamente.`,
                    timer: 1500,
                    showConfirmButton: false
                });
                siguientePregunta();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Error al rechazar la pregunta'
                });
            }
        } catch (error) {
            console.error('Error al rechazar:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error de conexión al rechazar la pregunta'
            });
        }
    });

    document.getElementById('btnRevisar')?.addEventListener('click', async function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        if (!comentarios.trim()) {
            Swal.fire({
                icon: 'warning',
                title: 'Observaciones requeridas',
                text: 'Por favor, ingresa las modificaciones sugeridas.'
            });
            return;
        }

        try {
            const response = await fetch(`/evaluador/api/enviar-revision-pregunta/${preguntaActual}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    curso_id: obtenerCursoIdActual(),
                    comentarios: comentarios,
                    iteracion: '1',
                    fecha_revision: new Date().toISOString()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Enviada a revisión',
                    text: `Pregunta #${preguntaActual} enviada a revisión correctamente.`,
                    timer: 1500,
                    showConfirmButton: false
                });
                siguientePregunta();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Error al enviar a revisión'
                });
            }
        } catch (error) {
            console.error('Error al enviar revisión:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error de conexión al enviar a revisión'
            });
        }
    });

    // Función auxiliar para obtener el curso_id actual
    function obtenerCursoIdActual() {
        const cursoItem = document.querySelector('.pendiente-item.activa');
        if (cursoItem) {
            return cursoItem.dataset.cursoId;
        }
        return document.body.dataset.cursoId || null;
    }

    // Función auxiliar para obtener CSRF token
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

    document.getElementById('btnOmitir')?.addEventListener('click', function () {
        console.log('Pregunta omitida:', preguntaActual);
        siguientePregunta();
    });

    function siguientePregunta() {
        if (preguntaActual < totalPreguntas) {
            preguntaActual++;
            actualizarContadores();
            actualizarPreguntaActiva();
            document.getElementById('comentariosValidacion').value = '';
        } else {
            alert('¡Has revisado todas las preguntas pendientes!');
        }
    }

    // Filtros
    document.getElementById('filtroPrioridad')?.addEventListener('change', function () {
        console.log('Filtrando por prioridad:', this.value);
    });

    document.getElementById('filtroAsignatura')?.addEventListener('change', function () {
        console.log('Filtrando por asignatura:', this.value);
    });

    document.getElementById('filtroOrden')?.addEventListener('change', function () {
        console.log('Ordenando por:', this.value);
    });

    // Botones de la barra de herramientas
    document.getElementById('btnModoRapido')?.addEventListener('click', function () {
        this.classList.toggle('btn-primary');
        this.classList.toggle('btn-success');
        const modoRapido = this.classList.contains('btn-success');
        console.log('Modo rápido:', modoRapido ? 'ACTIVADO' : 'DESACTIVADO');
    });

    document.getElementById('btnFiltrarIA')?.addEventListener('click', function () {
        this.classList.toggle('btn-outline');
        this.classList.toggle('btn-primary');
        console.log('Filtrar solo IA:', this.classList.contains('btn-primary'));
    });

    document.getElementById('btnFiltrarHumanas')?.addEventListener('click', function () {
        this.classList.toggle('btn-outline');
        this.classList.toggle('btn-primary');
        console.log('Filtrar solo humanas:', this.classList.contains('btn-primary'));
    });
});