
const userButton = document.getElementById('userButton');
const menuDropdown = document.getElementById('menuDropdown');

userButton.addEventListener('click', () => {
    menuDropdown.classList.toggle('active');
});

// Ocultar el menú si se hace clic fuera de él
document.addEventListener('click', (event) => {
    if (!userButton.contains(event.target) && !menuDropdown.contains(event.target)) {
        menuDropdown.classList.remove('active');
    }
});
