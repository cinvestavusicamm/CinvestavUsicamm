from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging
import random

logger = logging.getLogger(__name__)

class LoginSecurityService:
    MAX_INTENTOS = 5

    BLOQUEOS_PROGRESIVOS = [
        300,
        900,
        1800,
        3600,
        7200,
    ]

    HISTORIAL_BLOQUEOS_TTL = 60 * 60 * 24
    INTENTOS_TTL = 60 * 15

    @staticmethod
    def obtener_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    @classmethod
    def _key_intentos_ip(cls, ip):
        return f"login_attempts:ip:{ip}"

    @classmethod
    def _key_bloqueo_ip(cls, ip):
        return f"login_blocked:ip:{ip}"
    
    @classmethod
    def _key_historial_bloqueos_ip(cls, ip):
        return f"login_block_history:ip:{ip}"
    
    @classmethod
    def _key_tiempo_bloqueo(cls, ip):
        return f"login_block_time:ip:{ip}"

    @classmethod
    def _key_intentos_usuario(cls, curp):
        return f"login_attempts:user:{curp}"

    @classmethod
    def esta_bloqueado(cls, curp, ip):
        return bool(cache.get(cls._key_bloqueo_ip(ip)))

    @classmethod
    def registrar_fallo(cls, curp, ip):
        if cls.esta_bloqueado(None, ip):
            return
        
        key_ip = cls._key_intentos_ip(ip)
        key_user = cls._key_intentos_usuario(curp)
        
        intentos_ip = cache.get(key_ip, 0) + 1
        intentos_user = cache.get(key_user, 0) + 1
        
        cache.set(key_ip, intentos_ip, cls.INTENTOS_TTL)
        cache.set(key_user, intentos_user, cls.INTENTOS_TTL)
        
        if intentos_ip >= cls.MAX_INTENTOS or intentos_user >= cls.MAX_INTENTOS:
            cls._bloquear_ip(ip)

    @classmethod
    def _bloquear_ip(cls, ip):
        key_historial = cls._key_historial_bloqueos_ip(ip)
        bloqueos_previos = cache.get(key_historial, 0)
        
        duracion = cls._obtener_duracion_bloqueo(bloqueos_previos)
        tiempo_expiracion = timezone.now() + timedelta(seconds=duracion)
        
        cache.set(cls._key_bloqueo_ip(ip), True, duracion)
        cache.set(cls._key_tiempo_bloqueo(ip), tiempo_expiracion, duracion)
        cache.set(key_historial, bloqueos_previos + 1, cls.HISTORIAL_BLOQUEOS_TTL)
        
        cache.delete(cls._key_intentos_ip(ip))

    @classmethod
    def _obtener_duracion_bloqueo(cls, cantidad_bloqueos):
        indice = min(cantidad_bloqueos, len(cls.BLOQUEOS_PROGRESIVOS) - 1)
        variacion = random.uniform(0.8, 1.2)
        return int(cls.BLOQUEOS_PROGRESIVOS[indice] * variacion)

    @classmethod
    def limpiar_intentos(cls, curp, ip):
        cache.delete(cls._key_intentos_ip(ip))
        cache.delete(cls._key_intentos_usuario(curp))