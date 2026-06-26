const userButton = document.getElementById('userButton');
const menuDropdown = document.getElementById('menuDropdown');

userButton.addEventListener('click', () => {
    const abierto = menuDropdown.classList.toggle('active');
    userButton.setAttribute('aria-expanded', abierto);
    if (abierto) {
        const primerEnlace = menuDropdown.querySelector('a');
        if (primerEnlace) primerEnlace.focus();
    }
});

// Cerrar con Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menuDropdown.classList.contains('active')) {
        menuDropdown.classList.remove('active');
        userButton.setAttribute('aria-expanded', 'false');
        userButton.focus();
    }
});

// Navegación con flechas dentro del dropdown
menuDropdown.addEventListener('keydown', (e) => {
    const items = Array.from(menuDropdown.querySelectorAll('a'));
    const idx = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        const next = items[idx + 1] || items[0];
        next.focus();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prev = items[idx - 1] || items[items.length - 1];
        prev.focus();
    }
});

// Ocultar el menú si se hace clic fuera de él
document.addEventListener('click', (event) => {
    if (!userButton.contains(event.target) && !menuDropdown.contains(event.target)) {
        menuDropdown.classList.remove('active');
        userButton.setAttribute('aria-expanded', 'false');
    }
});

// ARIA inicial
userButton.setAttribute('aria-haspopup', 'true');
userButton.setAttribute('aria-expanded', 'false');
menuDropdown.setAttribute('role', 'menu');
menuDropdown.querySelectorAll('a').forEach(a => a.setAttribute('role', 'menuitem'));