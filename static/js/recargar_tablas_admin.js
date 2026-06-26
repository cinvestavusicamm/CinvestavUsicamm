function recargarTablas() {
    const urlParams = new URLSearchParams(window.location.search);
    const pageAdmins = urlParams.get('page_admins') || 1;
    const pageDocentes = urlParams.get('page_docentes') || 1;
    
    window.location.href = `?page_admins=${pageAdmins}&page_docentes=${pageDocentes}`;
}

