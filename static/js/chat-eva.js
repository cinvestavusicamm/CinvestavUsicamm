// ===== CHATBOT FUNCTIONALITY =====

document.addEventListener('DOMContentLoaded', function() {
    const btnChatbot = document.getElementById('btn-chatbot');
    const ventanaChatbot = document.getElementById('ventana-chatbot');
    const btnCerrarChatbot = document.getElementById('btn-cerrar-chatbot');
    const btnEnviar = document.getElementById('btn-enviar-mensaje-chatbot');
    const mensajeInput = document.getElementById('mensaje-input-chatbot');
    const mensajesContainer = document.getElementById('mensajes-chatbot');

    // Estado del chatbot
    let chatbotAbierto = false;

    // Función para abrir el chatbot
    function abrirChatbot() {
        ventanaChatbot.classList.remove('ventana-oculto-chatbot');
        ventanaChatbot.classList.add('ventana-visible-chatbot');
        chatbotAbierto = true;
        mensajeInput.focus();
    }

    // Función para cerrar el chatbot
    function cerrarChatbot() {
        ventanaChatbot.classList.remove('ventana-visible-chatbot');
        ventanaChatbot.classList.add('ventana-oculto-chatbot');
        chatbotAbierto = false;
    }

    // Función para alternar el chatbot (abrir/cerrar)
    function alternarChatbot() {
        if (chatbotAbierto) {
            cerrarChatbot();
        } else {
            abrirChatbot();
        }
    }

    // Función para agregar un mensaje al chat
    function agregarMensaje(texto, tipo) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.classList.add(tipo === 'usuario' ? 'mensaje-usuario' : 'mensaje-bot');
        mensajeDiv.textContent = texto;
        mensajesContainer.appendChild(mensajeDiv);
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }

    // Función para mostrar indicador de escritura
    function mostrarIndicadorEscritura() {
        const indicadorDiv = document.createElement('div');
        indicadorDiv.classList.add('indicador-escritura');
        indicadorDiv.id = 'indicador-escritura';
        indicadorDiv.innerHTML = 'Escribiendo<span>.</span><span>.</span><span>.</span>';
        mensajesContainer.appendChild(indicadorDiv);
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }

    // Función para ocultar indicador de escritura
    function ocultarIndicadorEscritura() {
        const indicador = document.getElementById('indicador-escritura');
        if (indicador) {
            indicador.remove();
        }
    }

    // Función para enviar mensaje
    async function enviarMensaje() {
        const mensaje = mensajeInput.value.trim();
        
        if (mensaje === '') return;

        // Agregar mensaje del usuario al chat
        agregarMensaje(mensaje, 'usuario');
        
        // Limpiar input
        mensajeInput.value = '';

        // Mostrar indicador de escritura
        mostrarIndicadorEscritura();

        try {
            // Aquí puedes conectar con tu API de chatbot
            // Por ahora, simulamos una respuesta
            setTimeout(() => {
                ocultarIndicadorEscritura();
                
                // Respuesta simulada del chatbot
                let respuesta = obtenerRespuestaSimulada(mensaje);
                agregarMensaje(respuesta, 'bot');
            }, 1000);
            
        } catch (error) {
            ocultarIndicadorEscritura();
            agregarMensaje('Lo siento, hubo un error. Por favor, intenta de nuevo.', 'bot');
        }
    }

    // Función para obtener respuesta simulada (puedes reemplazar con tu API)
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
            return 'Claro, puedo ayudarte con: \n- Gestionar evaluaciones\n- Banco de preguntas\n- Validaciones\n- Reportes y estadísticas\n- Calendario de actividades\n¿Sobre qué tema necesitas ayuda?';
        } else {
            return 'Gracias por tu mensaje. Un asesor revisará tu consulta. Mientras tanto, ¿puedo ayudarte con algo más sobre las evaluaciones?';
        }
    }

    // Función para manejar tecla Enter
    function manejarEnter(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            enviarMensaje();
        }
    }

    // Eventos
    if (btnChatbot) {
        btnChatbot.addEventListener('click', alternarChatbot);
    }

    if (btnCerrarChatbot) {
        btnCerrarChatbot.addEventListener('click', cerrarChatbot);
    }

    if (btnEnviar) {
        btnEnviar.addEventListener('click', enviarMensaje);
    }

    if (mensajeInput) {
        mensajeInput.addEventListener('keypress', manejarEnter);
    }

    // Cerrar chatbot al hacer click fuera (opcional)
    document.addEventListener('click', function(event) {
        if (chatbotAbierto && ventanaChatbot && btnChatbot) {
            // Si el click no es dentro del chatbot ni en el botón, cerrar
            if (!ventanaChatbot.contains(event.target) && !btnChatbot.contains(event.target)) {
                cerrarChatbot();
            }
        }
    });

    // Mensaje de bienvenida al cargar la página (solo si el chatbot está abierto)
    function mostrarMensajeBienvenida() {
        setTimeout(() => {
            if (chatbotAbierto) {
                agregarMensaje('¡Bienvenido a EscalafonIA! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?', 'bot');
            }
        }, 500);
    }

    // Opcional: Mostrar mensaje de bienvenida la primera vez que se abre
    let primeraVez = true;
    const abrirChatbotOriginal = abrirChatbot;
    abrirChatbot = function() {
        abrirChatbotOriginal();
        if (primeraVez) {
            setTimeout(() => {
                agregarMensaje('¡Hola! Soy el asistente de EscalafonIA. ¿En qué puedo ayudarte?', 'bot');
            }, 300);
            primeraVez = false;
        }
    };
    
    // Reemplazar la función original
    window.abrirChatbot = abrirChatbot;
});