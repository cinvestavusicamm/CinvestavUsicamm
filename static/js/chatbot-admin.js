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

        const botMsg = document.createElement("div");
        botMsg.className = "msg msg-bot";
        botMsg.innerText = "Jaguar está pensando...";
        chatBox.appendChild(botMsg);

        fetch(agenteAjaxURL, {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                pregunta: mensaje
            })
        })
        .then(res => res.json())
        .then(data => {
            botMsg.innerText = data.answer || data.error || "No hubo respuesta";
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(() => {
            botMsg.innerText = "El asistente no está disponible";
        });
    }