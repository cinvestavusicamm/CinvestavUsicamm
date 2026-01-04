-- Tabla ROLES
-- Define si es Docente, Analista, Administrador, etc.
CREATE TABLE roles (
    id_rol SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL
);

-- Tabla INSTITUCIONES
-- Define de dónde viene el usuario (CINVESTAV, USICAM, etc.)
CREATE TABLE instituciones (
    id_institucion SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(50),
    domicilio TEXT,
    claves varchar (150)not null  --claves SEP    
);

-- Tabla USUARIOS
-- Conecta con Roles e Instituciones mediante llaves foráneas (REFERENCES)
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) UNIQUE NOT NULL, -- UNIQUE para que no se repitan correos
    contraseña TEXT NOT NULL,
    rol_id INT REFERENCES roles(id_rol),
    institucion_id INT REFERENCES instituciones(id_institucion),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLA ESTADO
CREATE TABLE IF NOT EXISTS Estados (
	id_estado SERIAL PRIMARY KEY,
	clave_estados VARCHAR(4),
	nombre VARCHAR(100) NOT NULL 
);

-- Tabla MUNICIPIOS
CREATE TABLE IF NOT EXISTS Municipios (
	id_municipio SERIAL PRIMARY KEY,
	estado_id INT REFERENCES Estados(id_estado),
	clave_municipio VARCHAR(4),
	nombre VARCHAR(50)
);

-- Tabla CP (Código Postal)
CREATE TABLE IF NOT EXISTS Cp (
	id_cp SERIAL PRIMARY KEY,
	cp VARCHAR(5) NOT NULL, 
	municipio_id INT REFERENCES Municipios(id_municipio),
	zona VARCHAR(20) 
);

--Colonia
CREATE TABLE IF NOT EXISTS Colonia (
	id_colonia SERIAL PRIMARY KEY,
	nombre VARCHAR(50),
	cp_id INT REFERENCES Cp(id_cp)
);
--tipos de hogares
--hogares rurales y urbanos
CREATE TABLE IF NOT EXISTS Tipo_hogar (
	id_tipoH SERIAL PRIMARY KEY,
	nombre VARCHAR(50)
);

-- Relaciones geográficas
CREATE TABLE Direccion (
	id_direccion SERIAL PRIMARY KEY,
	calle VARCHAR(150) NOT NULL,
	numero_exterior VARCHAR(20),
	numero_interior VARCHAR(20),
		estado_id INT REFERENCES Estados(id_estado),
	municipio_id INT REFERENCES Municipios(id_municipio),
	cp_id INT REFERENCES Cp(id_cp),
	tipoH_id INT REFERENCES Tipo_hogar(id_tipoH)
);

-- Tabla NORMATIVAS (Biblioteca de PDFs)

CREATE TABLE normativas (
    id_norma SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_publicacion DATE,
    documento_pdf VARCHAR(255)
);

-- Tabla CONSULTAS (Historial del chat con el Agente)
CREATE TABLE consultas (
    id_consulta SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id_usuario),
    texto_usuario TEXT NOT NULL,
    respuesta_ia TEXT,
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    categoria VARCHAR(50)
);

-- Tabla VALIDACIONES
CREATE TABLE validaciones (
    id_validacion SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id_usuario),
    documento VARCHAR(255),
    resultado BOOLEAN, -- TRUE = Válido / FALSE = Inválido
    observaciones TEXT,
    fecha_validacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*
-- Tabla para guardar los "pedazos" vectorizados de tus normativas
CREATE TABLE normativas_vectores (
    id_vector SERIAL PRIMARY KEY,
    
    -- 1. Relación con tu tabla original (Foreign Key)
    -- Si borras la norma, se borran sus vectores automáticamente (ON DELETE CASCADE)
    norma_id INT REFERENCES normativas(id_norma) ON DELETE CASCADE,
    
    -- 2. El texto real del fragmento (para que la IA sepa qué leer)
    contenido_fragmento TEXT NOT NULL,
    
    -- 3. La "huella digital" numérica (El vector)
    -- Usamos 768 dimensiones, común en modelos locales de Ollama
    embedding vector(768),
    
    -- 4. Metadatos extra útiles (opcional, pero recomendado)
    numero_pagina INT, -- Para saber de qué página salió
    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear un índice especial para búsquedas rápidas (HNSW)
-- Esto hace que la búsqueda sea veloz incluso con millones de datos
CREATE INDEX ON normativas_vectores USING hnsw (embedding vector_cosine_ops);
*/


CREATE TABLE normativas_vectores (
    id_vector SERIAL PRIMARY KEY,
    norma_id INT REFERENCES normativas(id_norma) ON DELETE CASCADE,
    contenido_fragmento TEXT NOT NULL,
    embedding vector(768), 
    numero_pagina INT,
    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON normativas_vectores USING hnsw (embedding vector_cosine_ops);

--se agregan las columnas "claves" y "activo" en tabla "instituciones"
ALTER TABLE instituciones 
ADD COLUMN IF NOT EXISTS claves VARCHAR(150),
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;

-- se agregan las columnas "curp", "apellido_paterno", "apellido_materno", "activo", "ultimo_acceso" y 
--"direccion_id" a la tabla "usuarios"
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS curp CHAR(18) UNIQUE,
ADD COLUMN IF NOT EXISTS apellido_paterno VARCHAR(50), 
ADD COLUMN IF NOT EXISTS apellido_materno VARCHAR(50), 
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS ultimo_acceso TIMESTAMP,
ADD COLUMN IF NOT EXISTS direccion_id INT REFERENCES Direccion(id_direccion); 


select * from normativas;
TRUNCATE TABLE normativas, normativas_vectores RESTART IDENTITY CASCADE;

SELECT version();
SELECT * FROM pg_extension WHERE extname = 'vector';



SELECT * FROM pg_extension WHERE extname = 'vector';
SELECT 
    rolname AS "Nombre Usuario",
    rolsuper AS "Es Superusuario",
    rolcreaterole AS "Puede Crear Roles",
    rolcreatedb AS "Puede Crear DBs"
FROM pg_roles
WHERE rolname = current_user;