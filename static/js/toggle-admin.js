function cambiarEstado(id, elem) {
    fetch(`/administrador/toggle-usuario/${id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        // toggle_usuario responde con respuesta_ok/respuesta_error, que usan
        // estado/mensaje/datos. Este JS leia success/error, que esa funcion
        // nunca devuelve: por eso el boton nunca actualizaba nada y solo
        // mostraba "undefined".
        if (!ok || data.estado === 'error') {
            alert(data.mensaje || 'No se pudo cambiar el estado del usuario');
            return;
        }

        const activo = data.datos.activo;

        // Cambiar icono y color
        if (activo) {
            elem.classList.remove('fa-toggle-off');
            elem.classList.add('fa-toggle-on');
            elem.style.color = '#27AE60'; // verde
        } else {
            elem.classList.remove('fa-toggle-on');
            elem.classList.add('fa-toggle-off');
            elem.style.color = '#C0392B'; // rojo
        }

        // Actualizar contadores
        if (data.datos.contadores) {
            document.querySelector('[data-total]').textContent = data.datos.contadores.total;
            document.querySelector('[data-activos]').textContent = data.datos.contadores.activos;
            document.querySelector('[data-en-revision]').textContent = data.datos.contadores.en_revision;
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
