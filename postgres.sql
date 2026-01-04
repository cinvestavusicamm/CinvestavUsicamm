SELECT version();


SELECT 
    rolname AS "Nombre Usuario",
    rolsuper AS "Es Superusuario",
    rolcreaterole AS "Puede Crear Roles",
    rolcreatedb AS "Puede Crear DBs"
FROM pg_roles
WHERE rolname = current_user;



CREATE EXTENSION IF NOT EXISTS vector;

SELECT * FROM pg_extension WHERE extname = 'vector';

-- 1. Crear el usuario con su contraseña
CREATE USER admin_agentbd WITH PASSWORD 'XXXX';

-- 2. Permitirle conectarse a la base de datos 'postgres'
GRANT CONNECT ON DATABASE postgres TO admin_agentbd;

-- 3. Dar permiso de usar el esquema 'public'
GRANT USAGE ON SCHEMA public TO admin_agentbd;

-- 4. Permiso para CREAR tablas nuevas (Vital para agentes de IA que guardan memoria)
GRANT CREATE ON SCHEMA public TO admin_agentbd;

-- 5. Permisos para leer/escribir en las tablas que YA existen
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO admin_agentbd;

-- 6. Permisos para que funcionen los IDs automáticos (SERIAL)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_agentbd;

-- 7. Verificación final: Confirmar que el usuario se creó
SELECT usename FROM pg_catalog.pg_user WHERE usename = 'admin_agentbd';

-- Crear la base de datos y asignar al usuario como dueño inmediato
CREATE DATABASE db_escalofonia OWNER admin_agentbd;


