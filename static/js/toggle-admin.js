function cambiarEstado(id, elem) {
    fetch(`/toggle-usuario/${id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            alert(data.error);
            return;
        }

        // Cambiar icono y color
        if (data.activo) {
            elem.classList.remove('fa-toggle-off');
            elem.classList.add('fa-toggle-on');
            elem.style.color = '#27AE60'; // verde
        } else {
            elem.classList.remove('fa-toggle-on');
            elem.classList.add('fa-toggle-off');
            elem.style.color = '#C0392B'; // rojo
        }

        // Actualizar contadores
        if (data.contadores) {
            document.querySelector('[data-total]').textContent = data.contadores.total;
            document.querySelector('[data-activos]').textContent = data.contadores.activos;
            document.querySelector('[data-en-revision]').textContent = data.contadores.en_revision;
        }
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}
