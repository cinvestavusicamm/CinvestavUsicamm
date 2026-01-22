const barra = document.querySelector('.barra-lateral'); // Trae por clase
const fondo = document.getElementById('fondo');         // Trae por ID
const boton = document.getElementById('btn-menu');      // Trae por ID

boton.addEventListener('click', accionarMenu)

function accionarMenu() {
    barra.classList.toggle('mostrar');
    fondo.classList.toggle('activo');
}
fondo.addEventListener('click', accionarMenu);

// Detectar página actual y marcar enlace como activo
document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".barra-lateral-link");
    // Obtenemos el nombre del archivo actual (ej: UsuariosAdmin.php)
    const nombrePaginaActual = window.location.pathname.split("/").pop();

    links.forEach(link => {
        const href = link.getAttribute("href");
        
        // Validamos que el href no sea solo "#" y coincida con la página
        if (href !== "#" && href === nombrePaginaActual) {
            link.classList.add("activo");
        }
    });
});