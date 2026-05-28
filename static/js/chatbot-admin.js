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
    botText.textContent = "Jacqui pensando";
    botContainer.appendChild(botText);
    chatBox.appendChild(botContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    let textoCompleto = "";
    let thinkingInterval = setInterval(() => {
        let puntos = (botText.textContent.match(/\./g) || []).length;
        if (botText.textContent.includes("pensando")) {
            puntos = (puntos + 1) % 4;
            botText.textContent = "Jacqui pensando" + ".".repeat(puntos);
        }
    }, 500);

    console.log("Enviando petición a:", agenteAjaxURL);
    console.log("Mensaje:", mensaje);

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
    .then(async response => {
        console.log("Respuesta recibida, status:", response.status);
        console.log("Headers:", [...response.headers.entries()]);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                console.log("Stream completado");
                clearInterval(thinkingInterval);
                if (!textoCompleto) {
                    botText.textContent = "No se recibió respuesta";
                }
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            console.log("Chunk recibido:", chunk);
            buffer += chunk;

            const lines = buffer.split('\n\n');
            buffer = lines.pop() || "";

            for (const line of lines) {
                console.log("Procesando línea:", line);
                
                if (line.trim().startsWith("data:")) {
                    const rawData = line.substring(5).trim();
                    console.log("Raw data:", rawData);
                    
                    if (rawData && rawData !== "[DONE]") {
                        try {
                            const data = JSON.parse(rawData);
                            console.log("Datos parseados:", data);
                            
                            if (data.token !== undefined) {
                                if (botText.textContent.includes("pensando")) {
                                    clearInterval(thinkingInterval);
                                    botText.textContent = "";
                                }
                                textoCompleto += data.token;
                                botText.textContent = textoCompleto;
                                chatBox.scrollTop = chatBox.scrollHeight;
                            } else if (data.done === true) {
                                console.log("Stream marcado como done");
                                clearInterval(thinkingInterval);
                            } else if (data.error) {
                                console.error("Error del servidor:", data.error);
                                clearInterval(thinkingInterval);
                                botText.textContent = `Error: ${data.error}`;
                            }
                        } catch (e) {
                            console.error("Error parseando JSON:", e, rawData);
                        }
                    }
                }
            }
        }
    })
    .catch(error => {
        console.error('Error en fetch:', error);
        clearInterval(thinkingInterval);
        botText.textContent = "Error: No se pudo conectar con el asistente";
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