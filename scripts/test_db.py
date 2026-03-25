import asyncio
import asyncpg
import os

async def test_connection():
    try:
        # Usar la URL de Supabase
        DATABASE_URL = 'postgresql://postgres.ksdemhxapuhtmlgoknqw:admin_agent2025@aws-0-us-west-2.pooler.supabase.com:6543/postgres'
        print(f"Conectando a: {DATABASE_URL}")
        
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Conexión exitosa a Supabase!")
        
        # Probar una consulta simple
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Consulta de prueba: {result}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
