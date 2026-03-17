document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("chat-input");
    if (input) {
        input.addEventListener("keypress", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                enviarMensaje();
            }
        });
    }
});

let animacionActiva = false;

function enviarMensaje() {
    const input = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");
    const mensaje = input.value.trim();

    if (!mensaje) return;

    // Mensaje del usuario
    const userMsg = document.createElement("div");
    userMsg.className = "msg msg-user";
    userMsg.innerText = mensaje;
    chatBox.appendChild(userMsg);

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Crear contenedor para mensaje del bot con mejor estructura
    const botContainer = document.createElement("div");
    botContainer.className = "msg msg-bot";
    
    // Span para el texto
    const botText = document.createElement("span");
    botText.className = "bot-text";
    botText.innerText = "";
    botContainer.appendChild(botText);
    
    // Cursor animado
    const cursor = document.createElement("span");
    cursor.className = "typing-cursor";
    cursor.innerText = "▌";
    cursor.style.animation = "parpadeo 0.8s infinite";
    botContainer.appendChild(cursor);
    
    chatBox.appendChild(botContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Hacer la petición
    fetch(agenteAjaxURL, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            pregunta: mensaje,
            stream: "true"
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let textoCompleto = "";
        let buffer = "";

        function leerStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    // Terminar animación
                    cursor.style.display = "none";
                    botText.innerText = textoCompleto;
                    return;
                }

                const chunk = decoder.decode(value);
                buffer += chunk;
                
                // Procesar líneas completas
                const lines = buffer.split('\n');
                buffer = lines.pop() || "";
                
                lines.forEach(line => {
                    line = line.trim();
                    if (line.startsWith('data:')) {
                        const data = line.substring(5).trim();
                        if (data && data !== '[DONE]') {
                            try {
                                const parsed = JSON.parse(data);
                                
                                if (parsed.type === 'done') {
                                    cursor.style.display = "none";
                                    botText.innerText = textoCompleto;
                                } 
                                else if (parsed.type === 'error') {
                                    botText.innerText = "Error: " + parsed.message;
                                    cursor.style.display = "none";
                                } 
                                else if (parsed.token) {
                                    // Agregar el token de forma suave
                                    textoCompleto += parsed.token;
                                    botText.innerText = textoCompleto;
                                    chatBox.scrollTop = chatBox.scrollHeight;
                                }
                            } catch (e) {
                                // Si no es JSON, agregar como texto plano
                                textoCompleto += data;
                                botText.innerText = textoCompleto;
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                        }
                    }
                });

                leerStream();
            }).catch(error => {
                console.error('Error leyendo stream:', error);
                botText.innerText = textoCompleto || "Error en la transmisión";
                cursor.style.display = "none";
            });
        }

        leerStream();
    })
    .catch(error => {
        console.error('Error:', error);
        botContainer.innerHTML = "El asistente no está disponible";
    });
}

// Función para obtener el token CSRF
function getCsrfToken() {
    const name = 'csrftoken';
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