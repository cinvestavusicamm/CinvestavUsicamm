function abrirFormulario() {
    const form = document.getElementById('formUsuario');
    if (form) {
        form.reset();
    }
    document.getElementById('modalUsuario').style.display = 'flex';
}

function cerrarModal() {
    document.getElementById('modalUsuario').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formUsuario');
    
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        console.log('Datos a enviar:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Guardando...';
        submitBtn.disabled = true;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(agregarUsuarioURL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data);
            
            if (data.success) {
                alert('' + data.message);
                cerrarModal();
                location.reload(); 
            } else {
                let errorMsg = 'Error al crear usuario:\n\n';
                if (typeof data.error === 'string') {
                    errorMsg += data.error;
                } else if (typeof data.error === 'object') {
                    for (let campo in data.error) {
                        errorMsg += `${campo}: ${data.error[campo]}\n`;
                    }
                } else {
                    errorMsg += 'Error desconocido';
                }
                alert(errorMsg);
            }
        })
        .catch(error => {
            console.error('Error en fetch:', error);
            alert('Error de conexión con el servidor: ' + error.message);
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
});