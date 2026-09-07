const barra = document.querySelector('.barra-lateral');
const fondo = document.getElementById('fondo');
const boton = document.getElementById('btn-menu');

boton.addEventListener('click', accionarMenu);

function accionarMenu() {
    barra.classList.toggle('mostrar');
    fondo.classList.toggle('activo');
    const abierto = barra.classList.contains('mostrar');
    boton.setAttribute('aria-expanded', abierto);
}
fondo.addEventListener('click', accionarMenu);

// Cerrar barra lateral con Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && barra.classList.contains('mostrar')) {
        accionarMenu();
        boton.focus();
    }
});

// Detectar página actual y marcar enlace como activo
document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".barra-lateral-link");
    const nombrePaginaActual = window.location.pathname.split("/").pop();

    links.forEach(link => {
        const href = link.getAttribute("href");
        if (href !== "#" && href === nombrePaginaActual) {
            link.classList.add("activo");
        }
        // Navegación por teclado en menú lateral
        link.setAttribute('tabindex', '0');
    });

    // Navegación con flechas dentro del menú lateral
    const menuLinks = Array.from(document.querySelectorAll('.barra-lateral-link'));
    menuLinks.forEach((link, idx) => {
        link.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const next = menuLinks[idx + 1];
                if (next) next.focus();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                const prev = menuLinks[idx - 1];
                if (prev) prev.focus();
            }
        });
    });
});