from django.db.models import Count, Q

from apps.users.models import Curso, ProcesoEscalafon, Usuario


class RouterService:

    @staticmethod
    def decidir(pregunta: str):
        pregunta = (pregunta or "").lower()

        keywords_bd = [
            "plaza",
            "plazas",
            "docente",
            "docentes",
            "maestro",
            "maestros",
            "usuario",
            "usuarios",
            "registro",
            "datos",
            "curso",
            "cursos",
            "proceso",
            "procesos",
            "estatus",
            "estado",
            "estadistica",
            "estadísticas",
            "pendiente",
            "pendientes",
            "aprobado",
            "aprobados",
            "bd",
            "base de datos",
        ]

        for palabra in keywords_bd:
            if palabra in pregunta:
                return "bd"

        return "agente"

    @staticmethod
    def responder_desde_bd(pregunta: str, usuario_id=None):
        pregunta_normalizada = (pregunta or "").lower()
        partes = []

        if any(palabra in pregunta_normalizada for palabra in ("usuario", "usuarios", "docente")):
            total_usuarios = Usuario.objects.count()
            activos = Usuario.objects.filter(activo=True).count()
            partes.append(f"Usuarios registrados: {total_usuarios}. Activos: {activos}.")

        if any(palabra in pregunta_normalizada for palabra in ("curso", "cursos", "generador")):
            cursos = Curso.objects.all()
            if usuario_id and any(
                palabra in pregunta_normalizada for palabra in ("mis ", "mios", "míos", "creados")
            ):
                cursos = cursos.filter(docente_id=usuario_id)

            total_cursos = cursos.count()
            pendientes = cursos.filter(
                Q(estado__icontains="pendiente")
                | Q(estado__icontains="revision")
                | Q(estado__icontains="revisión")
            ).count()
            aprobados = cursos.filter(estado__icontains="aprob").count()
            estados = ", ".join(
                f"{item['estado'] or 'Sin estado'}: {item['total']}"
                for item in cursos.values("estado").annotate(total=Count("id_curso")).order_by("estado")
            )
            partes.append(
                f"Cursos registrados: {total_cursos}. Pendientes: {pendientes}. "
                f"Aprobados: {aprobados}."
            )
            if estados:
                partes.append(f"Distribución por estado: {estados}.")

        if any(palabra in pregunta_normalizada for palabra in ("proceso", "procesos", "escalafon", "escalafón")):
            procesos = ProcesoEscalafon.objects.all()
            if usuario_id and any(
                palabra in pregunta_normalizada for palabra in ("mis ", "mio", "mío", "mi proceso")
            ):
                procesos = procesos.filter(usuario_id=usuario_id)

            total_procesos = procesos.count()
            estados_proceso = ", ".join(
                f"{item['estatus'] or 'Sin estatus'}: {item['total']}"
                for item in procesos.values("estatus")
                .annotate(total=Count("id"))
                .order_by("estatus")
            )
            partes.append(f"Procesos de escalafón registrados: {total_procesos}.")
            if estados_proceso:
                partes.append(f"Distribución por estatus: {estados_proceso}.")

        if not partes:
            partes.append(
                "Puedo consultar usuarios, cursos y procesos de escalafón en la base de datos. "
                "Prueba preguntando por totales, pendientes, aprobados o estatus."
            )

        return " ".join(partes)
