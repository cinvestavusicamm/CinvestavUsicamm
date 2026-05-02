import os 
from fastapi import Security, HTTPException, status 
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-Internal-Service-Key", auto_error=False)

# FAIL-FAST: Si no encuentra la llave en el .env, usa un default seguro o truena
INTERNAL_KEY = os.getenv("microAI", "clave_estricta_por_defecto_cambiar_en_prod")

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