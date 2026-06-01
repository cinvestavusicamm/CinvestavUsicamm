// Chatbot del Administrador - Jaguar IA
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    
    if (!chatInput || !chatBox) {
        console.error('Elementos del chatbot no encontrados');
        return;
    }
    
    // Función para enviar mensaje
    window.enviarMensaje = async function() {
        const mensaje = chatInput.value.trim();
        if (!mensaje) return;
        
        // Agregar mensaje del usuario
        agregarMensaje(mensaje, 'user');
        chatInput.value = '';
        
        // Mostrar indicador de carga
        const loadingId = agregarMensaje('Pensando...', 'bot', true);
        
        try {
            const response = await fetch(agenteAjaxURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `pregunta=${encodeURIComponent(mensaje)}&stream=false`
            });
            
            const data = await response.json();
            
            // Eliminar mensaje de carga
            const loadingElement = document.getElementById(loadingId);
            if (loadingElement) loadingElement.remove();
            
            if (data.success) {
                agregarMensaje(data.datos.answer, 'bot');
            } else {
                agregarMensaje('Error: ' + (data.mensaje || 'No se pudo obtener respuesta'), 'bot');
            }
        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            const loadingElement = document.getElementById(loadingId);
            if (loadingElement) loadingElement.remove();
            agregarMensaje('Error de conexión con el servidor', 'bot');
        }
    };
    
    // Función para agregar mensaje al chat
    function agregarMensaje(texto, tipo, isLoading = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg msg-${tipo}`;
        msgDiv.textContent = texto;
        
        if (isLoading) {
            const msgId = 'msg-' + Date.now();
            msgDiv.id = msgId;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            return msgId;
        }
        
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Event listener para Enter
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            enviarMensaje();
        }
    });
    
    // Función para obtener cookie CSRF
    function getCookie(name) {
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
});
