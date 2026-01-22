    const btnAddUser = document.getElementById('btnAddUser');
    const userModal = document.getElementById('userModal');
    const cancelModal = document.getElementById('cancelModal');
    const addUserForm = document.getElementById('addUserForm');
    const formMessage = document.getElementById('formMessage');

    btnAddUser.addEventListener('click', () => {
        userModal.style.display = 'flex';
        formMessage.innerHTML = '';
    });
    cancelModal.addEventListener('click', () => {
        userModal.style.display = 'none';
        addUserForm.reset();
        formMessage.innerHTML = '';
    });

    addUserForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = new FormData(addUserForm);

        fetch("{% url 'agregar_usuario_ajax' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.success){
                formMessage.style.color = 'green';
                formMessage.innerText = 'Usuario agregado correctamente';
                addUserForm.reset();
                // Aquí podrías actualizar la tabla de usuarios sin recargar
            } else {
                formMessage.style.color = 'red';
                formMessage.innerText = data.error || 'Ocurrió un error';
            }
        })
        .catch(error => {
            formMessage.style.color = 'red';
            formMessage.innerText = 'Error al enviar el formulario';
        });
    });
