-- Script de datos iniciales para pruebas
-- Ejecutar después de las migraciones

-- Insertar roles predeterminados
INSERT INTO roles (id_rol, nombre_rol) VALUES 
(1, 'ADMIN'),
(2, 'DOCENTE'),
(3, 'EVALUADOR'),
(4, 'GENERADOR')
ON CONFLICT (id_rol) DO NOTHING;

-- Insertar institución de prueba
INSERT INTO instituciones (id_institucion, nombre, tipo, activo) VALUES 
(1, 'Institución de Prueba', 'Educación Básica', true)
ON CONFLICT (id_institucion) DO NOTHING;

-- Insertar curso de prueba
INSERT INTO cursos (id_curso, titulo, descripcion, estado, generado_con_ia, version, fecha_creacion, contenido_json, docente_id) VALUES 
(1, 'Curso de Prueba', 'Este es un curso de prueba para el sistema', 'Borrador', false, 1, NOW(), '{"modulos": []}', 1)
ON CONFLICT (id_curso) DO NOTHING;