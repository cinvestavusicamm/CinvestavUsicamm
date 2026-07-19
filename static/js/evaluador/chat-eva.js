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

    function getCsrfToken() {
        const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : '';
    }

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
            const response = await fetch(agenteAjaxURL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    pregunta: mensaje,
                    stream: 'true'
                })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let textoCompleto = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;
                        
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.token) {
                                if (textoCompleto === '') {
                                    ocultarIndicadorEscritura();
                                }
                                textoCompleto += parsed.token;
                                // Actualizar el último mensaje del bot
                                const mensajesBot = mensajesContainer.querySelectorAll('.mensaje-bot');
                                const ultimoMensaje = mensajesBot[mensajesBot.length - 1];
                                if (ultimoMensaje) {
                                    ultimoMensaje.textContent = textoCompleto;
                                } else {
                                    agregarMensaje(textoCompleto, 'bot');
                                }
                                mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
                            }
                        } catch (e) {
                            console.error('Error parseando JSON:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error);
            ocultarIndicadorEscritura();
            agregarMensaje('Lo siento, hubo un error. Por favor, intenta de nuevo.', 'bot');
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