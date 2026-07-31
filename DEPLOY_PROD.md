# Guía de Despliegue en Producción - CinvestavUsicamm Backend

Esta guía proporciona los pasos exactos para desplegar el proyecto "CinvestavUsicamm-back-end" en un servidor Ubuntu en la nube.

## Requisitos Previos

- Servidor Ubuntu 20.04+ con acceso SSH
- Al menos 8GB RAM y 4 CPU cores
- Al menos 50GB de espacio en disco
- Usuario con privilegios sudo

---

## Paso 1: Instalación de Dependencias Iniciales

Conéctate al servidor via SSH:

```bash
ssh usuario@tu-servidor.com
```

Actualiza el sistema e instala dependencias:

```bash
# Actualizar paquetes del sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias esenciales
sudo apt install -y \
    curl \
    wget \
    git \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    gnupg \
    lsb-release
```

---

## Paso 2: Instalación de Docker y Docker Compose

Instalar Docker:

```bash
# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Configurar repositorio estable de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar e iniciar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Agregar usuario actual al grupo docker (requiere logout/login después)
sudo usermod -aG docker $USER
```

**Importante:** Después de agregar el usuario al grupo docker, cierra sesión y vuelve a entrar para que los cambios surtan efecto.

---

## Paso 3: Clonar el Repositorio

Clona el repositorio del proyecto:

```bash
# Navegar al directorio donde deseas clonar el proyecto
cd /opt  # o tu directorio preferido

# Clonar el repositorio (reemplaza con tu URL real)
sudo git clone https://github.com/tu-usuario/CinvestavUsicamm-back-end.git

# Dar permisos al usuario actual sobre el directorio
sudo chown -R $USER:$USER /opt/CinvestavUsicamm-back-end

# Navegar al directorio del proyecto
cd /opt/CinvestavUsicamm-back-end
```

---

## Paso 4: Configurar Variables de Entorno

Crea el archivo `.env.prod` con las variables de entorno de producción:

```bash
# Crear archivo .env.prod desde el ejemplo
cp .env.example .env.prod

# Editar el archivo con tus valores de producción
nano .env.prod
```

**Variables críticas a configurar:**

```bash
# Base de datos
POSTGRES_USER=tu_usuario_seguro
POSTGRES_PASSWORD=tu_password_seguro_muy_largo
POSTGRES_DB=cinvestav_db

# Django
SECRET_KEY=tu_secret_key_muy_seguro_y_aleatorio
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,localhost

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Microservicios
AI_AGENT_SERVICE_URL=http://ms_ai_agent_service:8107
API_GATEWAY_URL=http://ms_api_gateway:8100
```

**Generar SECRET_KEY seguro:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Paso 5: Configurar Firewall (UFW)

Configura el firewall para permitir solo puertos necesarios:

```bash
# Habilitar firewall
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar estado
sudo ufw status
```

---

## Paso 6: Ejecutar Despliegue Automatizado

El proyecto incluye un script de despliegue automatizado que maneja todo el proceso:

```bash
# Dar permisos de ejecución al script (si no lo tiene)
chmod +x deploy.sh

# Ejecutar despliegue completo
./deploy.sh
```

**Opciones del script:**

```bash
# Despliegue sin backup de base de datos
./deploy.sh --no-backup

# Despliegue sin actualizar código desde Git
./deploy.sh --skip-update

# Ver ayuda
./deploy.sh --help
```

**El script automáticamente:**
- ✅ Verifica directorio y permisos de Docker
- ✅ Crea backup de la base de datos
- ✅ Actualiza código desde Git
- ✅ Construye imágenes Docker (--no-cache)
- ✅ Levanta contenedores en modo detached
- ✅ Ejecuta migraciones de Django
- ✅ Recolecta archivos estáticos
- ✅ Verifica health checks de servicios críticos
- ✅ Limpia imágenes Docker huérfanas
- ✅ Muestra resumen del despliegue

---

## Paso 7: Verificar Despliegue

Verifica que todos los servicios estén corriendo correctamente:

```bash
# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Verificar health checks
curl http://localhost/health
curl http://localhost:8100/health
```

---

## Comandos Útiles de Mantenimiento

### Ver Logs

```bash
# Logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f django
docker-compose -f docker-compose.prod.yml logs -f ms_ai_agent_service
docker-compose -f docker-compose.prod.yml logs -f ms_orchestrator
```

### Reiniciar Servicios

```bash
# Reiniciar todos los servicios
docker-compose -f docker-compose.prod.yml restart

# Reiniciar un servicio específico
docker-compose -f docker-compose.prod.yml restart django
docker-compose -f docker-compose.prod.yml restart ms_api_gateway
```

### Detener Servicios

```bash
# Detener todos los servicios
docker-compose -f docker-compose.prod.yml down

# Detener y eliminar volúmenes (cuidado: borra datos)
docker-compose -f docker-compose.prod.yml down -v
```

### Actualizar Despliegue

```bash
# Ejecutar despliegue actualizado
./deploy.sh
```

### Backup Manual de Base de Datos

```bash
# Crear backup manual
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_manual_$(date +%Y%m%d_%H%M%S).sql
```

### Monitoreo de Recursos

```bash
# Ver uso de recursos de contenedores
docker stats

# Ver espacio en disco
df -h

# Ver uso de Docker
docker system df
```

### Limpieza de Docker

```bash
# Limpiar imágenes huérfanas
docker image prune -f

# Limpiar contenedores detenidos
docker container prune -f

# Limpiar volúmenes no utilizados
docker volume prune -f

# Limpieza completa del sistema Docker
docker system prune -a -f
```

---

## Configuración de Logging

Los contenedores están configurados con límites de logging para evitar llenar el disco:

- **max-size:** 10MB por archivo de log
- **max-file:** 3 archivos de log por contenedor (30MB total por contenedor)

Esto se aplica a todos los servicios críticos:
- nginx
- postgres
- redis
- qdrant
- django
- celery_worker
- celery_beat
- ms_api_gateway
- ms_ai_agent_service
- ms_orchestrator
- backend_api

---

## Solución de Problemas

### Error: "Permission denied" al ejecutar Docker

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y volver a entrar
```

### Error: "No space left on device"

```bash
# Limpiar Docker
docker system prune -a -f

# Limpiar logs antiguos
docker-compose -f docker-compose.prod.yml logs --tail=0 > /dev/null
```

### Error: Contenedores no inician

```bash
# Ver logs de contenedores con problemas
docker-compose -f docker-compose.prod.yml logs

# Verificar estado de servicios
docker-compose -f docker-compose.prod.yml ps -a
```

### Error: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté saludable
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U ${POSTGRES_USER}

# Reiniciar PostgreSQL
docker-compose -f docker-compose.prod.yml restart postgres
```

---

## Seguridad Adicional

### Configurar SSL/TLS (Let's Encrypt)

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática está configurada por defecto
```

### Configurar Fail2Ban

```bash
# Instalar fail2ban
sudo apt install -y fail2ban

# Configurar para proteger SSH
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Monitoreo Recomendado

Considera instalar herramientas de monitoreo:

```bash
# Instalar htop para monitoreo de recursos
sudo apt install -y htop

# Instalar net-tools para diagnóstico de red
sudo apt install -y net-tools
```

---

## Soporte

Para problemas o preguntas:
- Revisar logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Verificar health checks: `curl http://localhost/health`
- Revisar documentación del proyecto

---

**Última actualización:** 2026-07-18
**Versión:** 1.0
