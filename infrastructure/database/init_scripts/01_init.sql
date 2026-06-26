-- Habilitar extensión de vectores (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear tabla de documentos
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source VARCHAR(255),
    embedding vector(768) -- 768 es la dimensión de nomic-embed-text
);