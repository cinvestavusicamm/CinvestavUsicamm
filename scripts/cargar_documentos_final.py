#!/usr/bin/env python3
import asyncio
import asyncpg
import httpx
import json
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = 'postgresql://postgres.ksdemhxapuhtmlgoknqw:admin_agent2025@aws-0-us-west-2.pooler.supabase.com:6543/postgres'
OLLAMA_URL = 'http://motor_ollama:11434/v1/embeddings'

DOCUMENTOS = [
    {
        "titulo": "¿Qué es USICAMM?",
        "contenido": """
USICAMM (tambien escrito como usicamm)significa Unidad del Sistema para la Carrera de las Maestras y los Maestros.

Es el organismo encargado de:
- Regular el ingreso al servicio docente
- Gestionar las promociones horizontales y verticales
- Administrar los cambios de centro de trabajo
- Coordinar las evaluaciones docentes

Fue creada para garantizar procesos transparentes en la carrera docente.
"""
    },
    {
        "titulo": "Trámites USICAMM",
        "contenido": """
Trámites principales en USICAMM:
- Registro inicial: CURP, identificación oficial, título
- Promoción horizontal: avance dentro de la misma categoría
- Promoción vertical: cambio a categoría superior
- Cambio de centro de trabajo
- Actualización de datos personales y académicos
"""
    },
    {
        "titulo": "Aprendizaje vertical",
        "contenido": """
El aprendizaje vertical se refiere a la progresión en profundidad de conocimientos, construyendo sobre conceptos previos de manera jerárquica.

En el contexto docente, implica:
- Dominio progresivo de contenidos
- Especialización en áreas específicas
- Desarrollo de habilidades complejas
- Construcción de conocimiento sobre bases sólidas
"""
    },
    {
        "titulo": "Derechos docentes",
        "contenido": """
Los docentes tienen derecho a:
- Estabilidad laboral
- Formación continua
- Evaluaciones justas
- Promociones por méritos
- Licencias y prestaciones
- Jubilación con beneficios
"""
    },
    {
        "titulo": "Escalafón docente",
        "contenido": """
El escalafón docente ordena a los maestros según:
- Antigüedad: años de servicio
- Méritos: cursos, publicaciones, proyectos
- Evaluaciones: resultados de exámenes
- Puntaje acumulado

Se usa para promociones y cambios de centro.
"""
    }
]

async def get_embedding(texto):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": "nomic-embed-text",
                    "input": texto
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Retornar como lista de floats
                return data['data'][0]['embedding']
            else:
                logger.error(f"Error en embedding: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error en get_embedding: {e}")
        return None

async def cargar_documentos():
    logger.info("🚀 Iniciando carga de documentos...")
    
    try:
        # Conectar a BD con statement_cache_size=0 para PgBouncer
        conn = await asyncpg.connect(
            DATABASE_URL,
            statement_cache_size=0
        )
        logger.info("✅ Conectado a PostgreSQL (modo PgBouncer)")
        
        # Verificar si la tabla existe
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            )
        """)
        logger.info(f"📋 Tabla 'documents' existe: {result}")
        
        if not result:
            # Crear tabla si no existe
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await conn.execute("""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768),
                    source VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("✅ Tabla 'documents' creada")
        
        # Verificar conexión a Ollama
        try:
            test_embedding = await get_embedding("test")
            if test_embedding:
                logger.info(f"✅ Conexión a Ollama OK (dimensión: {len(test_embedding)})")
            else:
                logger.error("❌ No se pudo conectar a Ollama")
                return
        except Exception as e:
            logger.error(f"❌ Error conectando a Ollama: {e}")
            return
        
        # Limpiar documentos existentes
        await conn.execute("DELETE FROM documents;")
        logger.info("🗑️ Documentos anteriores eliminados")
        
        for i, doc in enumerate(DOCUMENTOS):
            logger.info(f"⏳ Procesando {i+1}/{len(DOCUMENTOS)}: {doc['titulo']}")
            
            # Generar embedding
            texto_completo = f"{doc['titulo']}\n{doc['contenido']}"
            embedding = await get_embedding(texto_completo)
            
            if embedding:
                # Convertir la lista a un array de PostgreSQL
                # PostgreSQL espera el formato: '[0.1, 0.2, 0.3]'
                embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
                
                # Guardar en BD usando el formato correcto
                await conn.execute("""
                    INSERT INTO documents (content, embedding, source)
                    VALUES ($1, $2::vector, $3)
                """, doc['contenido'], embedding_str, doc['titulo'])
                
                logger.info(f"✅ {i+1}/{len(DOCUMENTOS)}: {doc['titulo']}")
            else:
                logger.error(f"❌ Error con embedding para: {doc['titulo']}")
        
        # Verificar
        count = await conn.fetchval("SELECT COUNT(*) FROM documents")
        logger.info(f"📊 Total documentos en BD: {count}")
        
        # Verificar un documento de ejemplo
        example = await conn.fetchrow("SELECT id, source, left(content, 50) as preview FROM documents LIMIT 1")
        if example:
            logger.info(f"📄 Ejemplo: {example['source']} - {example['preview']}...")
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return
    
    logger.info("✅ Carga completada!")

if __name__ == "__main__":
    asyncio.run(cargar_documentos())
