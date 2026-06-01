function abrirModalEditar() {
    document.getElementById('modalEditarUsuario').style.display = 'flex';
}

function cerrarModalEditar() {
    document.getElementById('modalEditarUsuario').style.display = 'none';
}

function editarUsuario(id) {
    console.log('Editando usuario ID:', id);
    
    const modal = document.getElementById('modalEditarUsuario');
    
    fetch(`/administrador/usuario/${id}/obtener/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('Respuesta status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Datos recibidos:', data);
        
        if (data.success) {
            const form = document.getElementById('formEditarUsuario');
            
            form.elements['id_usuario'].value = data.id_usuario;
            form.elements['nombre'].value = data.nombre || '';
            form.elements['apellido_paterno'].value = data.apellido_paterno || '';
            form.elements['apellido_materno'].value = data.apellido_materno || '';
            form.elements['correo'].value = data.correo || '';
            form.elements['curp'].value = data.curp || '';
            
            if (form.elements['rol']) {
                form.elements['rol'].value = data.rol;
            }
            
            if (form.elements['institucion']) {
                form.elements['institucion'].value = data.institucion;
            }
            
            if (form.elements['contrasena']) {
                form.elements['contrasena'].value = '';
            }
            
            abrirModalEditar();
        } else {
            alert('Error al cargar datos: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cargar los datos del usuario: ' + error.message);
    });
}

function enviarEdicionUsuario(id) {
    const form = document.getElementById('formEditarUsuario');
    const formData = new FormData(form);
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : 'Guardar';
    if (submitBtn) {
        submitBtn.textContent = 'Guardando...';
        submitBtn.disabled = true;
    }
    
    console.log('Enviando edición para usuario ID:', id);
    
    fetch(`/administrador/usuario/${id}/editar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => {
        console.log('Respuesta status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Respuesta:', data);
        
        if (data.success) {
            alert('Usuario actualizado correctamente');
            cerrarModalEditar();
            location.reload();
        } else {
            let errorMsg = 'Error al actualizar:\n\n';
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
        console.error('Error:', error);
        alert('Error de conexión: ' + error.message);
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const formEditar = document.getElementById('formEditarUsuario');
    if (formEditar) {
        const newForm = formEditar.cloneNode(true);
        formEditar.parentNode.replaceChild(newForm, formEditar);
        
        newForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const idUsuario = document.getElementById('edit_id').value;
            if (idUsuario) {
                enviarEdicionUsuario(idUsuario);
            } else {
                alert('Error: No se encontró el ID del usuario');
            }
        });
    }
});