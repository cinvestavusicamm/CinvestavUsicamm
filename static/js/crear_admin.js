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

        fetch(agregarUsuarioURL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                formMessage.style.color = 'green';
                formMessage.innerText = 'Usuario agregado correctamente';
                addUserForm.reset();
            } else {
                formMessage.style.color = 'red';
                formMessage.innerText = JSON.stringify(data.error);
            }
        })
        .catch(() => {
            formMessage.style.color = 'red';
            formMessage.innerText = 'Error del servidor';
        });
    });
