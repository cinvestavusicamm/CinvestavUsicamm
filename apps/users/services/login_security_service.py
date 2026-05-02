from django.core.cache import cache


class LoginSecurityService:
    MAX_INTENTOS = 5

    BLOQUEOS_PROGRESIVOS = [
        60,        # 1 minuto
        60 * 5,    # 5 minutos
        60 * 15,   # 15 minutos
        60 * 30,   # 30 minutos
    ]

    HISTORIAL_BLOQUEOS_TTL = 60 * 60 * 24  # 24 horas

    @staticmethod
    def obtener_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "")

    @classmethod
    def _key_curp(cls, curp):
        return f"login_attempts:curp:{curp}"

    @classmethod
    def _key_ip(cls, ip):
        return f"login_attempts:ip:{ip}"

    @classmethod
    def _key_bloqueo_curp(cls, curp):
        return f"login_blocked:curp:{curp}"

    @classmethod
    def _key_bloqueo_ip(cls, ip):
        return f"login_blocked:ip:{ip}"

    @classmethod
    def _key_historial_curp(cls, curp):
        return f"login_block_history:curp:{curp}"

    @classmethod
    def _key_historial_ip(cls, ip):
        return f"login_block_history:ip:{ip}"

    @classmethod
    def _obtener_duracion_bloqueo(cls, cantidad_bloqueos):
        indice = min(cantidad_bloqueos, len(cls.BLOQUEOS_PROGRESIVOS) - 1)
        return cls.BLOQUEOS_PROGRESIVOS[indice]

    @classmethod
    def esta_bloqueado(cls, curp, ip):
        return bool(
            cache.get(cls._key_bloqueo_curp(curp))
            or cache.get(cls._key_bloqueo_ip(ip))
        )

    @classmethod
    def registrar_fallo(cls, curp, ip):
        key_curp = cls._key_curp(curp)
        key_ip = cls._key_ip(ip)

        intentos_curp = cache.get(key_curp, 0) + 1
        intentos_ip = cache.get(key_ip, 0) + 1

        cache.set(key_curp, intentos_curp, cls.HISTORIAL_BLOQUEOS_TTL)
        cache.set(key_ip, intentos_ip, cls.HISTORIAL_BLOQUEOS_TTL)

        if intentos_curp >= cls.MAX_INTENTOS:
            cls._bloquear_curp(curp)

        if intentos_ip >= cls.MAX_INTENTOS:
            cls._bloquear_ip(ip)

    @classmethod
    def _bloquear_curp(cls, curp):
        key_historial = cls._key_historial_curp(curp)
        bloqueos_previos = cache.get(key_historial, 0)

        duracion = cls._obtener_duracion_bloqueo(bloqueos_previos)

        cache.set(cls._key_bloqueo_curp(curp), True, duracion)
        cache.set(key_historial, bloqueos_previos + 1, cls.HISTORIAL_BLOQUEOS_TTL)
        cache.delete(cls._key_curp(curp))

    @classmethod
    def _bloquear_ip(cls, ip):
        key_historial = cls._key_historial_ip(ip)
        bloqueos_previos = cache.get(key_historial, 0)

        duracion = cls._obtener_duracion_bloqueo(bloqueos_previos)

        cache.set(cls._key_bloqueo_ip(ip), True, duracion)
        cache.set(key_historial, bloqueos_previos + 1, cls.HISTORIAL_BLOQUEOS_TTL)
        cache.delete(cls._key_ip(ip))

    @classmethod
    def limpiar_intentos(cls, curp, ip):
        cache.delete(cls._key_curp(curp))
        cache.delete(cls._key_ip(ip))
        cache.delete(cls._key_bloqueo_curp(curp))
        cache.delete(cls._key_bloqueo_ip(ip))
