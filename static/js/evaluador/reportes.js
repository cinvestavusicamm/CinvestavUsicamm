// ===== REPORTES: SELECTORES DE FECHA Y GENERACIÓN DE REPORTES =====

document.addEventListener('DOMContentLoaded', function () {

    // Inicializar selectores de fecha
    if (window.flatpickr) {
        flatpickr("#fecha-inicio", {
            locale: "es",
            dateFormat: "d/m/Y",
            defaultDate: "today",
            maxDate: "today"
        });

        flatpickr("#fecha-fin", {
            locale: "es",
            dateFormat: "d/m/Y",
            defaultDate: "today"
        });
    }

    // Manejo de generación de reportes
    const btnGenerarReporte = document.getElementById('btn-generar-reporte');
    if (btnGenerarReporte) {
        btnGenerarReporte.addEventListener('click', function () {
            const evaluacion = document.getElementById('select-evaluacion').value;
            const tipo = document.getElementById('select-tipo').value;

            // Simulación de carga de datos
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
            this.disabled = true;

            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-chart-bar"></i> Reporte Generado';
                this.disabled = false;

                // Mostrar notificación
                mostrarNotificacion('success', 'Reporte generado exitosamente');
            }, 1500);
        });
    }

    const btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', function () {
            // Limpiar todos los filtros
            document.querySelectorAll('.select-filtro, .input-fecha').forEach(element => {
                if (element.tagName === 'SELECT') {
                    element.selectedIndex = 0;
                } else {
                    element.value = '';
                }
            });
            mostrarNotificacion('info', 'Filtros limpiados');
        });
    }

    function mostrarNotificacion(tipo, mensaje) {
        // Eliminar notificaciones existentes
        const existingNotifications = document.querySelectorAll('.notificacion-global');
        existingNotifications.forEach(notif => notif.remove());

        // Crear notificación
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion-global notificacion-global-${tipo}`;
        
        const iconMap = {
            'success': 'fa-check-circle',
            'info': 'fa-info-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle'
        };
        
        notificacion.innerHTML = `
            <i class="fas ${iconMap[tipo] || 'fa-info-circle'}"></i>
            <span>${mensaje}</span>
            <button class="btn-cerrar-notificacion" onclick="this.closest('.notificacion-global').remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        document.body.appendChild(notificacion);

        // Animación de entrada
        setTimeout(() => notificacion.classList.add('mostrar'), 10);

        // Remover después de 3.5 segundos
        setTimeout(() => {
            notificacion.classList.remove('mostrar');
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.remove();
                }
            }, 400);
        }, 3500);
    }
});