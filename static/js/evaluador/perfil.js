// ===== PERFIL: COPIAR CURP AL PORTAPAPELES =====

document.addEventListener('DOMContentLoaded', function () {
    const btnCopiarCurp = document.getElementById('btn-copiar-curp');
    if (!btnCopiarCurp) return;

    btnCopiarCurp.addEventListener('click', function () {
        const curp = this.dataset.curp || '';
        copiarAlPortapapeles(curp, this);
    });
});

function copiarAlPortapapeles(texto, btn) {
    navigator.clipboard.writeText(texto).then(function () {
        const iconoOriginal = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-check"></i>';
        btn.classList.add('copiado');
        setTimeout(function () {
            btn.innerHTML = iconoOriginal;
            btn.classList.remove('copiado');
        }, 2000);
    }).catch(function (err) {
        console.error('Error al copiar: ', err);
    });
}