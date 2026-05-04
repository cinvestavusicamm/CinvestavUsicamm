from apps.users.models import BitacoraEvento

class BitacoraService:

    @staticmethod
    def registrar(usuario_id, tipo_evento, descripcion, request=None, detalles=None):
        ip = None

        if request:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()

        return BitacoraEvento.objects.create(
            usuario_id=usuario_id,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            ip_direccion=ip,
            detalles=detalles or {},

        )