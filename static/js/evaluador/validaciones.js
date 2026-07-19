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
    document.getElementById('btnAprobar')?.addEventListener('click', function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        console.log('Pregunta aprobada', {
            pregunta: preguntaActual,
            comentarios: comentarios
        });

        // Simular aprobación
        alert(`Pregunta #${preguntaActual} aprobada correctamente.`);
        siguientePregunta();
    });

    document.getElementById('btnRechazar')?.addEventListener('click', function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        if (!comentarios.trim()) {
            alert('Por favor, ingresa los motivos del rechazo en los comentarios.');
            return;
        }

        console.log('Pregunta rechazada', {
            pregunta: preguntaActual,
            comentarios: comentarios
        });

        alert(`Pregunta #${preguntaActual} rechazada.`);
        siguientePregunta();
    });

    document.getElementById('btnRevisar')?.addEventListener('click', function () {
        const comentarios = document.getElementById('comentariosValidacion').value;
        if (!comentarios.trim()) {
            alert('Por favor, ingresa las modificaciones sugeridas.');
            return;
        }

        console.log('Pregunta enviada a revisión', {
            pregunta: preguntaActual,
            comentarios: comentarios
        });

        alert(`Pregunta #${preguntaActual} enviada a revisión.`);
        siguientePregunta();
    });

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