// ===== CONFIGURACIÓN: TABS, CONTRASEÑA, TEMA Y MODALES =====

document.addEventListener('DOMContentLoaded', function () {

    // Tabs functionality
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const tabId = this.getAttribute('data-tab');

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.config-panel').forEach(p => p.classList.remove('active'));

            this.classList.add('active');
            document.getElementById(`panel-${tabId}`).classList.add('active');
        });
    });

    // Password strength checker
    const nuevaPass = document.getElementById('pass-nueva');
    const confirmPass = document.getElementById('pass-confirm');
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text');

    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
        if (password.match(/\d/)) strength++;
        if (password.match(/[^a-zA-Z\d]/)) strength++;

        const strengthLevels = ['Muy débil', 'Débil', 'Regular', 'Fuerte', 'Muy fuerte'];
        const colors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#2ecc71'];
        const widths = ['20%', '40%', '60%', '80%', '100%'];

        if (strengthBar) {
            strengthBar.style.width = widths[strength];
            strengthBar.style.backgroundColor = colors[strength];
            strengthText.textContent = strengthLevels[strength];
            strengthText.style.color = colors[strength];
        }

        return strength;
    }

    if (nuevaPass) {
        nuevaPass.addEventListener('input', function () {
            checkPasswordStrength(this.value);
            checkPasswordMatch();
        });
    }

    function checkPasswordMatch() {
        if (confirmPass && nuevaPass) {
            const matchHint = document.getElementById('pass-match-hint');
            if (confirmPass.value.length > 0) {
                if (nuevaPass.value === confirmPass.value) {
                    matchHint.innerHTML = '<i class="fa-solid fa-check-circle"></i> Las contraseñas coinciden';
                    matchHint.style.color = '#27ae60';
                } else {
                    matchHint.innerHTML = '<i class="fa-solid fa-xmark-circle"></i> Las contraseñas no coinciden';
                    matchHint.style.color = '#e74c3c';
                }
            } else {
                matchHint.innerHTML = '';
            }
        }
    }

    if (confirmPass) {
        confirmPass.addEventListener('input', checkPasswordMatch);
    }

    function obtenerCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content) {
            return meta.content;
        }
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    function guardarPerfil() {
        const correoInput = document.getElementById('perfilCorreo');
        const correo = correoInput ? correoInput.value.trim() : '';
        const telefonoInput = document.getElementById('perfilTelefono');
        const telefono = telefonoInput ? telefonoInput.value.trim() : '';

        const btnGuardarPerfil = document.getElementById('btn-guardar-perfil');
        if (btnGuardarPerfil) btnGuardarPerfil.disabled = true;

        fetch('/evaluador/api/actualizar-perfil/', {
            method: 'PUT',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCsrfToken(),
            },
            body: JSON.stringify({ correo, telefono }),
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'No se pudo actualizar el perfil');
                }
                mostrarNotificacion(data.mensaje || 'Perfil actualizado correctamente');
            })
            .catch(error => {
                console.error(error);
                mostrarNotificacion(error.message || 'Error actualizando perfil', 'error');
            })
            .finally(() => {
                if (btnGuardarPerfil) btnGuardarPerfil.disabled = false;
            });
    }

    function cambiarContrasena() {
        const passActualElem = document.getElementById('pass-actual');
        const passNuevaElem = document.getElementById('pass-nueva');
        const passConfirmElem = document.getElementById('pass-confirm');
        const passActual = passActualElem ? passActualElem.value : '';
        const passNueva = passNuevaElem ? passNuevaElem.value : '';
        const passConfirm = passConfirmElem ? passConfirmElem.value : '';

        if (!passActual) {
            mostrarNotificacion('Por favor ingresa tu contraseña actual', 'error');
            return;
        }

        if (!passNueva || passNueva.length < 8) {
            mostrarNotificacion('La nueva contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }

        if (passNueva !== passConfirm) {
            mostrarNotificacion('Las contraseñas no coinciden', 'error');
            return;
        }

        const btnActualizarContrasena = document.getElementById('btn-actualizar-contrasena');
        if (btnActualizarContrasena) btnActualizarContrasena.disabled = true;

        fetch('/evaluador/api/actualizar-contrasena/', {
            method: 'PUT',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCsrfToken(),
            },
            body: JSON.stringify({
                contrasena_actual: passActual,
                nueva_contrasena: passNueva,
                confirmar_contrasena: passConfirm,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'No se pudo actualizar la contraseña');
                }
                mostrarNotificacion(data.mensaje || 'Contraseña actualizada correctamente');
                if (passActualElem) passActualElem.value = '';
                if (passNuevaElem) passNuevaElem.value = '';
                if (passConfirmElem) passConfirmElem.value = '';
                if (strengthBar) strengthBar.style.width = '0%';
                if (strengthText) strengthText.textContent = '';
            })
            .catch(error => {
                console.error(error);
                mostrarNotificacion(error.message || 'Error actualizando contraseña', 'error');
            })
            .finally(() => {
                if (btnActualizarContrasena) btnActualizarContrasena.disabled = false;
            });
    }

    // Botón "Guardar Cambios" del perfil
    const btnGuardarPerfil = document.getElementById('btn-guardar-perfil');
    if (btnGuardarPerfil) {
        btnGuardarPerfil.addEventListener('click', guardarPerfil);
    }

    // Botón "Actualizar Contraseña"
    const btnActualizarContrasena = document.getElementById('btn-actualizar-contrasena');
    if (btnActualizarContrasena) {
        btnActualizarContrasena.addEventListener('click', cambiarContrasena);
    }

    // Theme selection - keyboard accessible + saves to AccessibilityManager
    document.querySelectorAll('.theme-option').forEach(option => {
        option.setAttribute('tabindex', '0');
        option.setAttribute('role', 'button');

        function selectTheme(opt) {
            const theme = opt.getAttribute('data-theme');
            document.querySelectorAll('.theme-option').forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            if (window.accessibilityManager) {
                window.accessibilityManager.state.darkTheme = (theme === 'dark');
                window.accessibilityManager.applySetting('darkTheme');
                window.accessibilityManager.saveSettings();
                window.accessibilityManager.updatePanelValues();
                const panelToggle = document.getElementById('acc-darkTheme');
                if (panelToggle) panelToggle.checked = (theme === 'dark');
                const configToggle = document.getElementById('darkTheme');
                if (configToggle) configToggle.checked = (theme === 'dark');
            } else {
                document.body.classList.toggle('dark-theme', theme === 'dark');
            }
            mostrarNotificacion(`Tema ${theme === 'light' ? 'claro' : 'oscuro'} aplicado`);
        }

        option.addEventListener('click', function () { selectTheme(this); });
        option.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectTheme(this);
            }
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                const next = this.nextElementSibling;
                if (next) next.focus();
            }
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                const prev = this.previousElementSibling;
                if (prev) prev.focus();
            }
        });
    });

    // Syncing theme visual state with AccessibilityManager on load
    function syncThemeVisual() {
        if (!window.accessibilityManager) return;
        const isDark = window.accessibilityManager.state.darkTheme;
        document.querySelectorAll('.theme-option').forEach(opt => {
            const theme = opt.getAttribute('data-theme');
            opt.classList.toggle('active', (theme === 'dark') === isDark);
        });
    }
    syncThemeVisual();

    // Notificaciones para cambios de accesibilidad (delegado al AccessibilityManager)
    window.addEventListener('accessibilityChanged', function (e) {
        const { key, value } = e.detail;
        const messages = {
            grayscale: value ? 'Escala de grises activada' : 'Escala de grises desactivada',
            highContrast: value ? 'Alto contraste activado' : 'Alto contraste desactivado',
            invertColors: value ? 'Inversión de colores activada' : 'Inversión de colores desactivada',
            darkTheme: value ? 'Tema oscuro activado' : 'Tema claro activado',
            readingMask: value ? 'Máscara de lectura activada' : 'Máscara de lectura desactivada',
            readingGuide: value ? 'Guía de lectura activada' : 'Guía de lectura desactivada',
            highlightLinks: value ? 'Enlaces resaltados' : 'Resaltado de enlaces desactivado',
            dyslexicFont: value ? 'Fuente para dislexia activada' : 'Fuente para dislexia desactivada',
            screenReader: value ? 'Lector de pantalla activado' : 'Lector de pantalla desactivado',
            lineSpacing: `Espaciado vertical ajustado a ${value}`,
            letterSpacing: `Espaciado horizontal ajustado a ${value}px`,
            fontSize: `Redimensionamiento ajustado a ${value}px`
        };
        if (key === 'darkTheme') {
            document.querySelectorAll('.theme-option').forEach(opt => {
                const theme = opt.getAttribute('data-theme');
                opt.classList.toggle('active', (theme === 'dark') === value);
            });
        }
        if (messages[key]) {
            mostrarNotificacion(messages[key], 'info');
        }
    });

    // Modal functions
    function cerrarModal() {
        const modal = document.getElementById('modalConfirmacion');
        if (modal) modal.classList.remove('active');
    }

    function mostrarNotificacion(mensaje, tipo = 'success') {
        const toast = document.getElementById('toastNotificacion');
        const toastMsg = document.getElementById('toastMensaje');
        const icon = toast?.querySelector('i');

        if (toastMsg) toastMsg.textContent = mensaje;

        if (icon) {
            if (tipo === 'error') {
                icon.className = 'fa-solid fa-circle-exclamation';
                toast.style.background = '#e74c3c';
            } else if (tipo === 'warning') {
                icon.className = 'fa-solid fa-triangle-exclamation';
                toast.style.background = '#f39c12';
            } else {
                icon.className = 'fa-solid fa-circle-check';
                toast.style.background = '#27ae60';
            }
        }

        if (toast) {
            toast.classList.add('active');
            setTimeout(() => {
                toast.classList.remove('active');
            }, 3000);
        }
    }

    // Botón "Cancelar" del modal de confirmación
    const btnCancelarModalConfirmacion = document.getElementById('btnCancelarModalConfirmacion');
    if (btnCancelarModalConfirmacion) {
        btnCancelarModalConfirmacion.addEventListener('click', cerrarModal);
    }

    // Close modal when clicking outside
    window.addEventListener('click', function (event) {
        const modal = document.getElementById('modalConfirmacion');
        if (event.target === modal) {
            cerrarModal();
        }
    });
});