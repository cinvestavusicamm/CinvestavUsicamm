import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-Internal-Service-Key", auto_error=False)

# Nombre canonico de la clave compartida: el mismo que lee Django
# (settings.INTERNAL_SERVICE_KEY) y el mismo que documenta .env.example.
#
# Antes se leia "microAI", una variable que no definia ningun docker-compose
# ni el .env.example, asi que siempre caia en el literal de respaldo de aqui.
# El nombre "MICROSERVICE_SECRET" que si aparecia en los compose no lo leia
# nadie. Funcionaba solo porque Django y este microservicio tenian la misma
# cadena escrita a mano dos veces.
#
# Sin valor por defecto a proposito. Un literal de repuesto permitiria que el
# servicio arrancara con una clave conocida por cualquiera que lea el
# repositorio, que es justo lo que hay que evitar. Fallar al arrancar es
# preferible a arrancar abierto.
INTERNAL_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

if not INTERNAL_KEY.strip():
    raise RuntimeError(
        "INTERNAL_SERVICE_KEY no esta definida. El microservicio de IA no "
        "arranca sin ella: es la clave que Django manda en la cabecera "
        "X-Internal-Service-Key y tiene que ser el mismo valor en los dos "
        "lados. Definela en el entorno (en los compose, "
        "${INTERNAL_SERVICE_KEY:?}) y en el .env. Genera una nueva con "
        "python -c \"import secrets; print(secrets.token_urlsafe(48))\": la "
        "anterior estaba escrita en el codigo y sigue en el historial de "
        "git, aunque ya no sirva para nada."
    )


async def verify_internal_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Verifica que la petición venga del sys django auth.
    """
    if not api_key or api_key != INTERNAL_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso Denegado. Credenciales de servicio inválidas."
        )
    return api_key