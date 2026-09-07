// ===== REPORTES: SELECTORES DE FECHA Y GENERACIÓN DE REPORTES =====

document.addEventListener('DOMContentLoaded', function () {

    // Inicializar selectores de fecha
    if (window.flatpickr) {
        flatpickr('#fecha-inicio', {
            locale: 'es',
            dateFormat: 'd/m/Y',
            defaultDate: 'today',
            maxDate: 'today',
        });

        flatpickr('#fecha-fin', {
            locale: 'es',
            dateFormat: 'd/m/Y',
            defaultDate: 'today',
            maxDate: 'today',
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

    function parseDate(value) {
        if (!value) return null;
        if (value.includes('-')) {
            const parsed = new Date(value);
            return Number.isNaN(parsed.getTime()) ? null : parsed;
        }
        const parts = value.split('/');
        if (parts.length === 3) {
            const day = parseInt(parts[0], 10);
            const month = parseInt(parts[1], 10) - 1;
            const year = parseInt(parts[2], 10);
            const parsed = new Date(year, month, day);
            return Number.isNaN(parsed.getTime()) ? null : parsed;
        }
        return null;
    }

    function getReportData() {
        let reportesBd = {};
        let reportesAdicionales = {};
        let evaluacionesBd = [];
        let aprobacionesBd = [];

        try {
            const reportesBdEl = document.getElementById('reportesBdData');
            const reportesAdicionalesEl = document.getElementById('reportesAdicionalesData');
            const evaluacionesEl = document.getElementById('evaluacionesBdFullData');
            const aprobacionesEl = document.getElementById('aprobacionesBdData');

            reportesBd = reportesBdEl ? JSON.parse(reportesBdEl.textContent) : {};
            reportesAdicionales = reportesAdicionalesEl ? JSON.parse(reportesAdicionalesEl.textContent) : {};
            evaluacionesBd = evaluacionesEl ? JSON.parse(evaluacionesEl.textContent) : [];
            aprobacionesBd = aprobacionesEl ? JSON.parse(aprobacionesEl.textContent) : [];
        } catch (error) {
            console.error('No se pudo parsear data de reportes:', error);
        }

        return { reportesBd, reportesAdicionales, evaluacionesBd, aprobacionesBd };
    }

    function groupBy(list, key) {
        return list.reduce((acc, item) => {
            const value = item[key] || 'Sin dato';
            if (!acc[value]) acc[value] = 0;
            acc[value] += 1;
            return acc;
        }, {});
    }

    function buildChartBars(cursosPorEstado) {
        const container = document.getElementById('barras-estado-container');
        const ejeEstado = document.getElementById('eje-estado');
        if (!container || !ejeEstado) return;

        if (!cursosPorEstado.length) {
            container.innerHTML = '<div class="grafico-simulado-empty">No hay datos de cursos</div>';
            ejeEstado.innerHTML = '';
            return;
        }

        const maxTotal = Math.max(...cursosPorEstado.map(item => item.total), 1);
        container.innerHTML = cursosPorEstado.map(item => {
            const width = Math.max(5, Math.round((item.total / maxTotal) * 100));
            return `
                <div class="barra-grafico" title="${item.estado}: ${item.total} cursos" style="width: ${width}%;">
                    <span class="barra-label">${item.estado} (${item.total})</span>
                </div>
            `;
        }).join('');

        ejeEstado.innerHTML = cursosPorEstado.map(item => `<span>${item.estado}</span>`).join('');
    }

    function buildDecisionList(decisiones) {
        const lista = document.getElementById('lista-decisiones');
        const leyenda = document.getElementById('leyenda-decisiones');
        if (!lista || !leyenda) return;

        if (!decisiones.length) {
            lista.innerHTML = '<li class="grafico-simulado-empty">No hay datos de decisiones</li>';
            leyenda.innerHTML = '<div class="item-leyenda">No hay decisiones registradas</div>';
            return;
        }

        lista.innerHTML = decisiones.map(item => `
            <li>
                <span class="decision-label">${item.decision || 'Sin decisión'}</span>
                <span class="decision-value">${item.total} (${item.percent || 0}%)</span>
            </li>
        `).join('');

        leyenda.innerHTML = decisiones.map(item => `
            <div class="item-leyenda">
                <span class="color-leyenda"></span>${item.decision || 'Sin decisión'}
            </div>
        `).join('');
    }

    function applyReportFilters() {
        const { evaluacionesBd, aprobacionesBd } = getReportData();
        const evaluacionId = document.getElementById('select-evaluacion')?.value;
        const tipoReporte = document.getElementById('select-tipo')?.value;
        const fechaInicio = parseDate(document.getElementById('fecha-inicio')?.value || '');
        const fechaFin = parseDate(document.getElementById('fecha-fin')?.value || '');
        const nivel = document.getElementById('select-nivel')?.value;
        const dimension = document.getElementById('select-dimension')?.value;
        const entidad = document.getElementById('select-entidad')?.value;

        let cursosFiltrados = [...evaluacionesBd];
        let aprobacionesFiltradas = [...aprobacionesBd];

        if (evaluacionId) {
            cursosFiltrados = cursosFiltrados.filter(c => String(c.id_curso) === evaluacionId);
            aprobacionesFiltradas = aprobacionesFiltradas.filter(a => String(a.curso_id) === evaluacionId);
        }

        if (fechaInicio || fechaFin) {
            cursosFiltrados = cursosFiltrados.filter(curso => {
                const fecha = parseDate(curso.fecha_creacion);
                if (!fecha) return false;
                if (fechaInicio && fecha < fechaInicio) return false;
                if (fechaFin && fecha > fechaFin) return false;
                return true;
            });
            aprobacionesFiltradas = aprobacionesFiltradas.filter(aprobacion => {
                const fecha = parseDate(aprobacion.fecha_revision);
                if (!fecha) return false;
                if (fechaInicio && fecha < fechaInicio) return false;
                if (fechaFin && fecha > fechaFin) return false;
                return true;
            });
        }

        if (nivel) {
            cursosFiltrados = cursosFiltrados.filter(curso => {
                const meta = curso.contenido_json || {};
                return String(meta.nivel || '').toLowerCase() === nivel.toLowerCase();
            });
        }

        if (dimension) {
            cursosFiltrados = cursosFiltrados.filter(curso => {
                const meta = curso.contenido_json || {};
                return String(meta.dimension || '').toLowerCase() === dimension.toLowerCase();
            });
        }

        if (entidad) {
            cursosFiltrados = cursosFiltrados.filter(curso => {
                const meta = curso.contenido_json || {};
                return String(meta.entidad || '').toLowerCase() === entidad.toLowerCase();
            });
        }

        const totalCursos = cursosFiltrados.length;
        const totalPendientes = cursosFiltrados.filter(c => /pendiente|revision|revisión/i.test(c.estado || '')).length;
        const totalAprobados = cursosFiltrados.filter(c => /aprob/i.test(c.estado || '')).length;
        const totalRechazados = cursosFiltrados.filter(c => /rechaz|no aprob/i.test(c.estado || '')).length;
        const totalBorradores = cursosFiltrados.filter(c => /borrador/i.test(c.estado || '')).length;
        const totalRevisiones = aprobacionesFiltradas.length;
        const tasaAprobacion = totalRevisiones ? Math.round((totalAprobados / totalRevisiones) * 10000) / 100 : 0;

        const estados = Object.entries(groupBy(cursosFiltrados, 'estado')).map(([estado, total]) => ({
            estado: estado || 'Sin estado',
            total,
        })).sort((a, b) => b.total - a.total);
        const maxTotal = estados.reduce((max, item) => Math.max(max, item.total), 1);
        estados.forEach(item => {
            item.bar_percent = Math.round(item.total * 100 / maxTotal);
        });

        const decisiones = Object.entries(groupBy(aprobacionesFiltradas, 'decision')).map(([decision, total]) => ({
            decision: decision || 'Sin decisión',
            total,
        }));
        const totalDecisiones = decisiones.reduce((sum, item) => sum + item.total, 0) || 1;
        decisiones.forEach(item => {
            item.percent = Math.round((item.total * 100 / totalDecisiones) * 100) / 100;
        });

        const report = {
            reportesBd: {
                total_revisiones: totalRevisiones,
                total_cursos: totalCursos,
                tasa_aprobacion: tasaAprobacion,
                total_pendientes: totalPendientes,
                total_aprobados: totalAprobados,
                total_rechazados: totalRechazados,
                total_borradores: totalBorradores,
                filtro_tipo: tipoReporte || 'general',
            },
            reportesAdicionales: {
                cursos_por_estado: estados,
                decisiones_por_tipo: decisiones,
            },
            evaluacionesFiltradas: cursosFiltrados,
            aprobacionesFiltradas: aprobacionesFiltradas,
        };

        updateReportDisplay(report);
        return report;
    }

    function updateReportDisplay(report) {
        document.getElementById('metric-total-revisiones').textContent = report.reportesBd.total_revisiones || 0;
        document.getElementById('metric-total-cursos').textContent = report.reportesBd.total_cursos || 0;
        document.getElementById('metric-tasa-aprobacion').textContent = `${report.reportesBd.tasa_aprobacion || 0}%`;

        buildChartBars(report.reportesAdicionales.cursos_por_estado || []);
        buildDecisionList(report.reportesAdicionales.decisiones_por_tipo || []);
        currentReport = report;
    }

    let currentReport = null;

    function applyReportFilterButton() {
        const button = document.getElementById('btn-generar-reporte');
        if (!button) return;

        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';

        setTimeout(() => {
            const report = applyReportFilters();
            button.disabled = false;
            button.innerHTML = originalText;
            mostrarNotificacion('success', `Reporte actualizado: ${report.reportesBd.total_cursos} cursos y ${report.reportesBd.total_revisiones} revisiones`);
        }, 300);
    }

    function clearFilters() {
        document.querySelectorAll('.select-filtro, .input-fecha').forEach(element => {
            if (element.tagName === 'SELECT') {
                element.selectedIndex = 0;
            } else {
                element.value = '';
            }
        });
        applyReportFilters();
        mostrarNotificacion('info', 'Filtros limpiados');
    }

    function exportPdfReport() {
        if (!currentReport) {
            currentReport = applyReportFilters();
        }
        const { reportesBd, reportesAdicionales } = currentReport;
        const doc = new window.jspdf.jsPDF();
        const margin = 14;
        let y = 20;

        doc.setFontSize(16);
        doc.text('Reporte Estadístico EscalafonIA', margin, y);
        y += 10;
        doc.setFontSize(11);
        doc.text('Resumen de métricas:', margin, y);
        y += 8;

        const metricas = [
            ['Revisiones registradas', reportesBd.total_revisiones || 0],
            ['Cursos / Evaluaciones', reportesBd.total_cursos || 0],
            ['Tasa de aprobación', `${reportesBd.tasa_aprobacion || 0}%`],
            ['Cursos pendientes', reportesBd.total_pendientes || 0],
            ['Cursos aprobados', reportesBd.total_aprobados || 0],
            ['Cursos rechazados', reportesBd.total_rechazados || 0],
            ['Cursos en borrador', reportesBd.total_borradores || 0],
        ];

        metricas.forEach(([label, value]) => {
            doc.text(`${label}: ${value}`, margin, y);
            y += 7;
            if (y > 275) {
                doc.addPage();
                y = margin;
            }
        });

        const cursosPorEstado = reportesAdicionales.cursos_por_estado || [];
        if (cursosPorEstado.length) {
            y += 10;
            doc.text('Cursos por estado:', margin, y);
            y += 8;
            cursosPorEstado.forEach(estado => {
                doc.text(`${estado.estado}: ${estado.total}`, margin, y);
                y += 7;
                if (y > 275) {
                    doc.addPage();
                    y = margin;
                }
            });
        }

        const decisiones = reportesAdicionales.decisiones_por_tipo || [];
        if (decisiones.length) {
            y += 10;
            doc.text('Decisiones por tipo:', margin, y);
            y += 8;
            decisiones.forEach(decision => {
                doc.text(`${decision.decision || 'Sin decisión'}: ${decision.total} (${decision.percent || 0}%)`, margin, y);
                y += 7;
                if (y > 275) {
                    doc.addPage();
                    y = margin;
                }
            });
        }

        const filename = `reporte_estadistico_${new Date().toISOString().slice(0, 10)}.pdf`;
        doc.save(filename);
        mostrarNotificacion('success', 'PDF generado y descargado');
    }

    function exportExcelReport() {
        if (!currentReport) {
            currentReport = applyReportFilters();
        }
        const { reportesBd, reportesAdicionales, evaluacionesFiltradas, aprobacionesFiltradas } = currentReport;
        const workbook = XLSX.utils.book_new();

        const resumenRows = [
            ['Métrica', 'Valor'],
            ['Revisiones registradas', reportesBd.total_revisiones || 0],
            ['Cursos / Evaluaciones', reportesBd.total_cursos || 0],
            ['Tasa de aprobación', `${reportesBd.tasa_aprobacion || 0}%`],
            ['Cursos pendientes', reportesBd.total_pendientes || 0],
            ['Cursos aprobados', reportesBd.total_aprobados || 0],
            ['Cursos rechazados', reportesBd.total_rechazados || 0],
            ['Cursos en borrador', reportesBd.total_borradores || 0],
        ];
        const wsResumen = XLSX.utils.aoa_to_sheet(resumenRows);
        XLSX.utils.book_append_sheet(workbook, wsResumen, 'Resumen');

        if ((reportesAdicionales.cursos_por_estado || []).length) {
            const estadoRows = [['Estado', 'Total', 'Porcentaje']];
            reportesAdicionales.cursos_por_estado.forEach(estado => {
                estadoRows.push([estado.estado, estado.total, `${estado.bar_percent || 0}%`]);
            });
            const wsEstado = XLSX.utils.aoa_to_sheet(estadoRows);
            XLSX.utils.book_append_sheet(workbook, wsEstado, 'Cursos por Estado');
        }

        if ((reportesAdicionales.decisiones_por_tipo || []).length) {
            const decisionRows = [['Decisión', 'Total', 'Porcentaje']];
            reportesAdicionales.decisiones_por_tipo.forEach(decision => {
                decisionRows.push([decision.decision || 'Sin decisión', decision.total, `${decision.percent || 0}%`]);
            });
            const wsDecisiones = XLSX.utils.aoa_to_sheet(decisionRows);
            XLSX.utils.book_append_sheet(workbook, wsDecisiones, 'Decisiones');
        }

        const cursosRows = [['ID curso', 'Título', 'Estado', 'Fecha creación', 'Fecha aprobación']];
        evaluacionesFiltradas.forEach(curso => {
            cursosRows.push([
                curso.id_curso,
                curso.titulo,
                curso.estado || '',
                curso.fecha_creacion || '',
                curso.fecha_aprobacion || '',
            ]);
        });
        const wsCursos = XLSX.utils.aoa_to_sheet(cursosRows);
        XLSX.utils.book_append_sheet(workbook, wsCursos, 'Cursos');

        const aprobacionesRows = [['ID proceso', 'Curso', 'Decisión', 'Fecha revisión', 'Iteración']];
        aprobacionesFiltradas.forEach(item => {
            aprobacionesRows.push([
                item.id_proceso,
                item.curso_titulo || '',
                item.decision || '',
                item.fecha_revision || '',
                item.iteracion || '',
            ]);
        });
        const wsAprobaciones = XLSX.utils.aoa_to_sheet(aprobacionesRows);
        XLSX.utils.book_append_sheet(workbook, wsAprobaciones, 'Aprobaciones');

        const filename = `reporte_estadistico_${new Date().toISOString().slice(0, 10)}.xlsx`;
        XLSX.writeFile(workbook, filename);
        mostrarNotificacion('success', 'Excel generado y descargado');
    }

    const btnExportarPdf = document.getElementById('btn-exportar-pdf');
    if (btnExportarPdf) {
        btnExportarPdf.addEventListener('click', exportPdfReport);
    }

    const btnExportarExcel = document.getElementById('btn-exportar-excel');
    if (btnExportarExcel) {
        btnExportarExcel.addEventListener('click', exportExcelReport);
    }

    const btnExportarPdfSection = document.getElementById('btn-exportar-pdf-section');
    if (btnExportarPdfSection) {
        btnExportarPdfSection.addEventListener('click', exportPdfReport);
    }

    const btnExportarExcelSection = document.getElementById('btn-exportar-excel-section');
    if (btnExportarExcelSection) {
        btnExportarExcelSection.addEventListener('click', exportExcelReport);
    }

    const btnGenerarReporte = document.getElementById('btn-generar-reporte');
    if (btnGenerarReporte) {
        btnGenerarReporte.addEventListener('click', applyReportFilterButton);
    }

    const btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', clearFilters);
    }

    applyReportFilters();
});