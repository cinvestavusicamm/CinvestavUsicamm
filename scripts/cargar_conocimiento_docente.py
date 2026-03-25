#!/usr/bin/env python3
# scripts/cargar_conocimiento_docente.py

import asyncio
import os
import sys
import asyncpg
import logging

# Agregamos rutas al path
sys.path.append('/app')
sys.path.append('/app/backend_api')
sys.path.append('/app/backend_api/src')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar vector_repo
try:
    from backend_api.src.infrastructure.persistence.agent.vector_repo import PostgresVectorRepo
    logger.info("✅ PostgresVectorRepo importado")
except ImportError as e:
    logger.error(f"❌ Error importando vector_repo: {e}")
    sys.exit(1)

# Importar OllamaAdapter (clase correcta)
try:
    from backend_api.src.infrastructure.external.agent.ollama import OllamaAdapter
    logger.info("✅ OllamaAdapter importado")
except ImportError as e:
    logger.error(f"❌ Error importando OllamaAdapter: {e}")
    sys.exit(1)

# ===== DOCUMENTOS SOBRE USICAMM =====
DOCUMENTOS_USICAMM = [
    {
        "titulo": "¿Qué es USICAMM?",
        "contenido": """
USICAMM significa **Unidad del Sistema para la Carrera de las Maestras y los Maestros**.

Es el organismo encargado de:
- Regular el **ingreso** al servicio docente
- Gestionar las **promociones** horizontales y verticales
- Administrar los **cambios de centro de trabajo**
- Coordinar las **evaluaciones** docentes
- Mantener el **Sistema de Información y Gestión Educativa**

Fue creada para garantizar procesos transparentes y meritocráticos en la carrera docente.
"""
    },
    {
        "titulo": "Trámites USICAMM más comunes",
        "contenido": """
**Trámites principales en USICAMM:**

1. **Registro inicial**: CURP, identificación oficial, comprobante de estudios, cédula profesional.

2. **Promoción horizontal**: Avance dentro de la misma categoría. Requiere:
   - Mínimo 2-4 años en la categoría actual
   - Puntaje mínimo en evaluación
   - Cursos de actualización

3. **Promoción vertical**: Cambio a categoría superior. Requiere:
   - Evaluación de conocimientos
   - Antigüedad mínima
   - Plazas disponibles

4. **Cambio de centro de trabajo**: Por:
   - Cercanía al domicilio
   - Razones de salud
   - Intercambio con otro docente

5. **Actualización de datos**: Cambios de:
   - Domicilio
   - Grado académico
   - Cursos y certificaciones
"""
    },
    {
        "titulo": "Documentos necesarios para USICAMM",
        "contenido": """
**Documentación básica para trámites USICAMM:**

- **CURP** actualizada
- **Identificación oficial** (INE, pasaporte)
- **Comprobante de domicilio** reciente
- **Título y cédula profesional**
- **Historial académico** (kardex)
- **Constancias de cursos** actualizados
- **Cartas de recomendación** (cuando aplique)
- **Comprobante de antigüedad** laboral
"""
    },
    {
        "titulo": "Evaluaciones USICAMM",
        "contenido": """
**Tipos de evaluación en USICAMM:**

1. **Evaluación de ingreso**: Para nuevos docentes
   - Examen de conocimientos
   - Habilidades didácticas
   - Competencias socioemocionales

2. **Evaluación de promoción**: Para ascensos
   - Portafolio de evidencias
   - Proyecto de mejora escolar
   - Examen de conocimientos especializados

3. **Evaluación diagnóstica**: Para identificar áreas de mejora
   - No punitiva
   - Identifica necesidades de formación

Los resultados determinan:
- Puntaje para promociones
- Elegibilidad para cambios
- Acceso a estímulos
"""
    },
]

# ===== DOCUMENTOS SOBRE ESTRATEGIAS DE ENSEÑANZA =====
DOCUMENTOS_PEDAGOGIA = [
    {
        "titulo": "Estrategias para mejorar tus clases",
        "contenido": """
**10 Estrategias para mejorar tus clases:**

1. **Aprendizaje basado en proyectos**: Los estudiantes aplican conocimientos a problemas reales.

2. **Gamificación**: Usa elementos de juego (puntos, niveles, recompensas) para motivar.

3. **Aula invertida**: Los estudiantes estudian teoría en casa y practican en clase.

4. **Trabajo colaborativo**: Grupos pequeños con roles definidos.

5. **Evaluación formativa**: Retroalimentación constante, no solo exámenes finales.

6. **Uso de tecnología**: Herramientas digitales, simuladores, recursos interactivos.

7. **Conexión con la vida real**: Relaciona contenidos con experiencias cotidianas.

8. **Diferenciación**: Adapta actividades a diferentes niveles y estilos de aprendizaje.

9. **Retroalimentación efectiva**: Específica, oportuna y orientada a la mejora.

10. **Clima positivo**: Crea un ambiente de confianza y respeto.
"""
    },
    {
        "titulo": "Técnicas de enseñanza activa",
        "contenido": """
**Técnicas de enseñanza activa:**

- **Phillips 66**: Grupos de 6 personas discuten 6 minutos y comparten conclusiones.

- **Estudio de casos**: Analizan situaciones reales para aplicar conocimientos.

- **Role playing**: Simulan situaciones para practicar habilidades.

- **Debate**: Discuten diferentes perspectivas sobre un tema.

- **Mapas conceptuales**: Organizan visualmente ideas y relaciones.

- **Puzzle de Aronson**: Cada estudiante se vuelve experto en un subtema y lo enseña.

- **Aprendizaje por descubrimiento**: Guía a estudiantes para que encuentren respuestas.

**Beneficios:**
- Mayor participación
- Mejor retención
- Desarrollo de pensamiento crítico
"""
    },
    {
        "titulo": "Cómo motivar a los estudiantes",
        "contenido": """
**Estrategias de motivación en el aula:**

1. **Conoce a tus estudiantes**: Intereses, estilos de aprendizaje, metas personales.

2. **Establece metas claras**: Objetivos específicos y alcanzables.

3. **Relevancia**: Muestra cómo lo aprendido se aplica en la vida real.

4. **Autonomía**: Da opciones y permite decisiones.

5. **Reconocimiento**: Celebra logros, no solo resultados finales.

6. **Retos adecuados**: Actividades desafiantes pero alcanzables.

7. **Retroalimentación positiva**: Destaca avances, no solo errores.

8. **Ambiente seguro**: Donde equivocarse es parte del aprendizaje.

9. **Variedad**: Cambia dinámicas y recursos regularmente.

10. **Ejemplo personal**: Muestra entusiasmo por tu materia.
"""
    },
    {
        "titulo": "Evaluación formativa vs sumativa",
        "contenido": """
**Diferencias entre evaluación formativa y sumativa:**

**Evaluación formativa:**
- Durante el proceso de aprendizaje
- Propósito: Mejorar y ajustar
- Ejemplos: Observaciones, tareas, preguntas en clase, portafolios
- Retroalimentación: Inmediata y específica
- No tiene calificación

**Evaluación sumativa:**
- Al final del proceso
- Propósito: Calificar y certificar
- Ejemplos: Exámenes finales, proyectos finales
- Retroalimentación: Generalmente solo calificación
- Tiene calificación

**Recomendación:** Combina ambas. Usa formativa para guiar y sumativa para evaluar resultados.
"""
    },
]

async def cargar_documentos():
    """Carga los documentos en PostgreSQL"""
    
    logger.info("🚀 Iniciando carga de documentos...")
    
    # Configurar servicios
    try:
        llm = OllamaAdapter()
        logger.info("✅ OllamaAdapter configurado")
    except Exception as e:
        logger.error(f"❌ Error configurando OllamaAdapter: {e}")
        return
    
    try:
        repo = PostgresVectorRepo()
        logger.info("✅ PostgresVectorRepo configurado")
    except Exception as e:
        logger.error(f"❌ Error configurando PostgresVectorRepo: {e}")
        return
    
    # Cargar documentos
    todos_documentos = DOCUMENTOS_USICAMM + DOCUMENTOS_PEDAGOGIA
    logger.info(f"📚 Cargando {len(todos_documentos)} documentos...")
    
    for i, doc in enumerate(todos_documentos):
        try:
            logger.info(f"⏳ Procesando {i+1}/{len(todos_documentos)}: {doc['titulo']}")
            
            # Generar embedding
            vector = await llm.get_embedding(doc['contenido'])
            
            # Guardar en PostgreSQL
            await repo.save_document(
                content=doc['contenido'],
                vector=vector,
                metadata={
                    "source": doc['titulo'],
                    "categoria": "usicamm" if i < len(DOCUMENTOS_USICAMM) else "pedagogia"
                }
            )
            logger.info(f"✅ {i+1}/{len(todos_documentos)}: {doc['titulo']}")
            
        except Exception as e:
            logger.error(f"❌ Error en {doc['titulo']}: {e}")
    
    # Verificar
    logger.info("\n=== 🔍 VERIFICANDO BÚSQUEDAS ===")
    
    pruebas = [
        "¿Qué es USICAMM?",
        "¿Cómo mejorar mis clases?",
        "Trámites USICAMM",
        "Motivación estudiantes"
    ]
    
    for prueba in pruebas:
        logger.info(f"\n🔎 Buscando: {prueba}")
        try:
            vector = await llm.get_embedding(prueba)
            resultados = await repo.search_similarity(vector, limit=2)
            
            if resultados:
                for j, res in enumerate(resultados):
                    logger.info(f"  📄 Resultado {j+1}: {res[:100]}...")
            else:
                logger.info("  ⚠️ No se encontraron resultados")
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
    
    logger.info("✅ Carga completada exitosamente!")

if __name__ == "__main__":
    asyncio.run(cargar_documentos())
