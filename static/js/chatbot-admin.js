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

function enviarMensaje() {
    const input = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");
    const mensaje = input.value.trim();

    if (!mensaje) return;

    const userMsg = document.createElement("div");
    userMsg.className = "msg msg-user";
    userMsg.innerText = mensaje;
    chatBox.appendChild(userMsg);

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    const botContainer = document.createElement("div");
    botContainer.className = "msg msg-bot";

    const botText = document.createElement("span");
    botText.className = "bot-text";
    botText.textContent = "";
    botText.style.whiteSpace = "pre-wrap";
    botContainer.appendChild(botText);

    const cursor = document.createElement("span");
    cursor.className = "typing-cursor";
    cursor.innerText = "▌";
    cursor.style.animation = "parpadeo 0.8s infinite";
    cursor.style.display = "none"; 
    botContainer.appendChild(cursor);

    chatBox.appendChild(botContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    let puntos = 0;
    botText.textContent = "Jacqui pensando";
    const thinkingInterval = setInterval(() => {
        puntos = (puntos + 1) % 4;
        botText.textContent = "Jacqui pensando" + ".".repeat(puntos);
    }, 500);

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
        let inicioRespuesta = false;

        function leerStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    clearInterval(thinkingInterval);
                    cursor.style.display = "none";
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                const lines = buffer.split('\n');
                buffer = lines.pop() || "";

                lines.forEach(line => {
                    line = line.trim();

                    if (line.startsWith("data:")) {
                        const rawData = line.substring(6);

                        if (rawData.trim() === "[DONE]") {
                            clearInterval(thinkingInterval);
                            cursor.style.display = "none";
                            return;
                        }

                        if (rawData.trim()) {
                            // Decodificar JSON para obtener el token exacto con espacios
                            let token;
                            try {
                                token = JSON.parse(rawData);
                            } catch(e) {
                                token = rawData;
                            }

                            if (!inicioRespuesta) {
                                inicioRespuesta = true;
                                clearInterval(thinkingInterval);
                                botText.textContent = "";
                                cursor.style.display = "inline";
                            }

                            textoCompleto += token;
                            botText.textContent = textoCompleto;
                            chatBox.scrollTop = chatBox.scrollHeight;
                        }
                    }
                });

                leerStream(); // ← Llamada recursiva dentro de la función
            }).catch(error => {
                console.error('Error leyendo stream:', error);
                clearInterval(thinkingInterval);
                botText.textContent = textoCompleto || "Error en la transmisión";
                cursor.style.display = "none";
            });
        }

        leerStream(); // ← Llamada inicial para comenzar el stream

    })
    .catch(error => {
        console.error('Error:', error);
        botContainer.innerHTML = "El asistente no está disponible";
    });
}

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