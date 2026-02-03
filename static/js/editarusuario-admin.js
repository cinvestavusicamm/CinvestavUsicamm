        function abrirModalEditar() {
            document.getElementById('modalEditarUsuario').style.display = 'flex';
        }

        function cerrarModalEditar() {
            document.getElementById('modalEditarUsuario').style.display = 'none';
        }

        function editarUsuario(id) {
            fetch(`/usuario/${id}/obtener/`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const form = document.getElementById('formEditarUsuario');
                        form.elements['id_usuario'].value = data.id_usuario;
                        form.elements['nombre'].value = data.nombre;
                        form.elements['apellido_paterno'].value = data.apellido_paterno;
                        form.elements['apellido_materno'].value = data.apellido_materno;
                        form.elements['correo'].value = data.correo;
                        form.elements['curp'].value = data.curp;
                        form.elements['rol'].value = data.rol;
                        form.elements['institucion'].value = data.institucion;
                        form.elements['contrasena'].value = '';

                        abrirModalEditar();

                        form.onsubmit = function (e) {
                            e.preventDefault();
                            enviarEdicionUsuario(id);
                        }
                    } else {
                        alert(data.error);
                    }
                });
        }

        function enviarEdicionUsuario(id) {
            const form = document.getElementById('formEditarUsuario');
            const formData = new FormData(form);

            fetch(`/usuario/${id}/editar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Usuario actualizado correctamente');
                        location.reload();
                    } else {
                        let errores = '';
                        if (typeof data.error === 'object') {
                            for (let campo in data.error) {
                                errores += `${campo}: ${data.error[campo]}\n`;
                            }
                        } else {
                            errores = data.error;
                        }
                        alert('Error: ' + errores);
                    }
                });
        }