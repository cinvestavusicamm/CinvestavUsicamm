# Microservicio de Base de Datos CINVESTAVUSICAMM

Este microservicio independiente proporciona acceso a la base de datos del proyecto CINVESTAVUSICAMM mediante APIs REST.

## Funcionalidades

- Obtener lista de usuarios
- Obtener lista de roles
- Obtener lista de instituciones
- Obtener detalles de un usuario específico

## Requisitos

- Python 3.11
- Acceso a la base de datos PostgreSQL configurada en `DATABASE_URL`

## Instalación y Ejecución

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variable de entorno:
   ```bash
   export DATABASE_URL="postgresql://user:password@host:port/dbname"
   ```

3. Ejecutar el servidor:
   ```bash
   python main.py
   ```

O usando Docker:
```bash
docker-compose up --build
```

## Endpoints

- `GET /`: Mensaje de bienvenida
- `GET /usuarios`: Lista de usuarios
- `GET /roles`: Lista de roles
- `GET /instituciones`: Lista de instituciones
- `GET /usuario/{id}`: Detalles de un usuario

## Notas

Este microservicio es completamente independiente y no modifica ningún archivo del proyecto original. Se conecta a la misma base de datos usando las credenciales proporcionadas.