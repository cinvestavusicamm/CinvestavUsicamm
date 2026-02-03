        function abrirFormulario() {
            document.getElementById('modalUsuario').style.display = 'flex';
        }

        function cerrarModal() {
            document.getElementById('modalUsuario').style.display = 'none';
        }

        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('formUsuario');

            form.addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(this);

                fetch(agregarUsuarioURL, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: formData
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            alert('Usuario creado correctamente');
                            location.reload();
                        } else {
                            let errores = '';
                            for (let campo in data.error) {
                                errores += `${campo}: ${data.error[campo].join(', ')}\n`;
                            }
                            alert(errores);
                        }
                    })
                    .catch(() => alert('Error del servidor'));
            });
        });