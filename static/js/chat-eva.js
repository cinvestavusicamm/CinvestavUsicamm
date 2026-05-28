// ===== CHATBOT FUNCTIONALITY =====

document.addEventListener('DOMContentLoaded', function() {
    const btnChatbot = document.getElementById('btn-chatbot');
    const ventanaChatbot = document.getElementById('ventana-chatbot');
    const btnCerrarChatbot = document.getElementById('btn-cerrar-chatbot');
    const btnEnviar = document.getElementById('btn-enviar-mensaje-chatbot');
    const mensajeInput = document.getElementById('mensaje-input-chatbot');
    const mensajesContainer = document.getElementById('mensajes-chatbot');

    let chatbotAbierto = false;
    let primeraVez = true;

    function abrirChatbot() {
        ventanaChatbot.classList.remove('ventana-oculto-chatbot');
        ventanaChatbot.classList.add('ventana-visible-chatbot');
        chatbotAbierto = true;
        mensajeInput.focus();
        ventanaChatbot.setAttribute('aria-hidden', 'false');

        if (primeraVez) {
            setTimeout(() => {
                agregarMensaje('¡Hola! Soy el asistente de EscalafonIA. ¿En qué puedo ayudarte?', 'bot');
            }, 300);
            primeraVez = false;
        }
    }

    function cerrarChatbot() {
        ventanaChatbot.classList.remove('ventana-visible-chatbot');
        ventanaChatbot.classList.add('ventana-oculto-chatbot');
        chatbotAbierto = false;
        ventanaChatbot.setAttribute('aria-hidden', 'true');
        btnChatbot.focus();
    }

    function alternarChatbot() {
        if (chatbotAbierto) {
            cerrarChatbot();
        } else {
            abrirChatbot();
        }
    }

    function agregarMensaje(texto, tipo) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.classList.add(tipo === 'usuario' ? 'mensaje-usuario' : 'mensaje-bot');
        mensajeDiv.textContent = texto;
        mensajeDiv.setAttribute('role', tipo === 'bot' ? 'status' : 'none');
        mensajesContainer.appendChild(mensajeDiv);
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }

    function mostrarIndicadorEscritura() {
        const indicadorDiv = document.createElement('div');
        indicadorDiv.classList.add('indicador-escritura');
        indicadorDiv.id = 'indicador-escritura';
        indicadorDiv.setAttribute('aria-live', 'polite');
        indicadorDiv.innerHTML = 'Escribiendo<span>.</span><span>.</span><span>.</span>';
        mensajesContainer.appendChild(indicadorDiv);
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }

    function ocultarIndicadorEscritura() {
        const indicador = document.getElementById('indicador-escritura');
        if (indicador) indicador.remove();
    }

    async function enviarMensaje() {
        const mensaje = mensajeInput.value.trim();
        if (mensaje === '') return;

        agregarMensaje(mensaje, 'usuario');
        mensajeInput.value = '';
        mostrarIndicadorEscritura();

        try {
            setTimeout(() => {
                ocultarIndicadorEscritura();
                const respuesta = obtenerRespuestaSimulada(mensaje);
                agregarMensaje(respuesta, 'bot');
            }, 1000);
        } catch (error) {
            ocultarIndicadorEscritura();
            agregarMensaje('Lo siento, hubo un error. Por favor, intenta de nuevo.', 'bot');
        }
    }

    function obtenerRespuestaSimulada(mensaje) {
        const mensajeLower = mensaje.toLowerCase();
        if (mensajeLower.includes('hola') || mensajeLower.includes('buenas')) {
            return '¡Hola! Soy el asistente de EscalafonIA. ¿En qué puedo ayudarte?';
        } else if (mensajeLower.includes('evaluaci') || mensajeLower.includes('evaluar')) {
            return 'Puedes gestionar tus evaluaciones desde la sección "Evaluaciones" en el menú lateral. ¿Necesitas ayuda con alguna evaluación en específico?';
        } else if (mensajeLower.includes('pregunta') || mensajeLower.includes('banco')) {
            return 'El banco de preguntas te permite gestionar todas las preguntas para tus evaluaciones. Puedes agregar, editar o eliminar preguntas según necesites.';
        } else if (mensajeLower.includes('validar') || mensajeLower.includes('validacion')) {
            return 'Las validaciones te permiten revisar y aprobar las evaluaciones realizadas. Revisa la sección "Validaciones" para ver los pendientes.';
        } else if (mensajeLower.includes('reporte') || mensajeLower.includes('estadistica')) {
            return 'Puedes generar reportes detallados desde la sección "Reportes". Allí encontrarás gráficos y análisis de las evaluaciones.';
        } else if (mensajeLower.includes('calendario') || mensajeLower.includes('fecha')) {
            return 'El calendario te ayuda a organizar tus evaluaciones y fechas importantes. Puedes ver todas tus actividades programadas allí.';
        } else if (mensajeLower.includes('ayuda') || mensajeLower.includes('ayudame')) {
            return 'Claro, puedo ayudarte con:\n- Gestionar evaluaciones\n- Banco de preguntas\n- Validaciones\n- Reportes y estadísticas\n- Calendario de actividades\n¿Sobre qué tema necesitas ayuda?';
        } else {
            return 'Gracias por tu mensaje. Un asesor revisará tu consulta. Mientras tanto, ¿puedo ayudarte con algo más sobre las evaluaciones?';
        }
    }

    // Eventos
    if (btnChatbot) btnChatbot.addEventListener('click', alternarChatbot);
    if (btnCerrarChatbot) btnCerrarChatbot.addEventListener('click', cerrarChatbot);
    if (btnEnviar) btnEnviar.addEventListener('click', enviarMensaje);
    if (mensajeInput) {
        mensajeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); enviarMensaje(); }
        });
    }

    // Cerrar con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && chatbotAbierto) cerrarChatbot();
    });

    // Cerrar al click fuera
    document.addEventListener('click', function(event) {
        if (chatbotAbierto && ventanaChatbot && btnChatbot) {
            if (!ventanaChatbot.contains(event.target) && !btnChatbot.contains(event.target)) {
                cerrarChatbot();
            }
        }
    });

    // ARIA
    if (ventanaChatbot) {
        ventanaChatbot.setAttribute('role', 'dialog');
        ventanaChatbot.setAttribute('aria-label', 'Chat de asistencia');
        ventanaChatbot.setAttribute('aria-hidden', 'true');
    }
    if (btnChatbot) {
        btnChatbot.setAttribute('aria-label', 'Abrir chat de asistencia');
    }
});