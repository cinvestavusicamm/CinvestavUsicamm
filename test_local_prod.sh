#!/bin/bash

# Script de prueba local para docker-compose.prod.yml
# Este script levanta el entorno de producción y ejecuta health checks automatizados

set -e

echo "=========================================="
echo "🚀 Iniciando prueba local de producción"
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Función para verificar health check
check_service_health() {
    local service_name=$1
    local container_name=$2
    local port=$3
    local endpoint=$4
    local max_attempts=30
    local attempt=1

    echo "Verificando $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:${port}${endpoint}" > /dev/null 2>&1; then
            print_success "$service_name está saludable"
            return 0
        fi
        echo "  Intento $attempt/$max_attempts: $service_name no responde..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name no pasó el health check después de $max_attempts intentos"
    return 1
}

# Función para verificar estado de contenedor
check_container_status() {
    local container_name=$1
    local status=$(docker ps --filter "name=$container_name" --format "{{.Status}}")
    
    if [ -z "$status" ]; then
        print_error "Contenedor $container_name no está corriendo"
        docker ps -a --filter "name=$container_name" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        return 1
    fi
    
    if [[ $status == *"Exited"* ]]; then
        print_error "Contenedor $container_name ha terminado con error"
        docker logs $container_name --tail 50
        return 1
    fi
    
    print_success "$container_name está corriendo: $status"
    return 0
}

# Paso 1: Verificar que docker-compose.prod.yml existe
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "docker-compose.prod.yml no encontrado"
    exit 1
fi

print_success "docker-compose.prod.yml encontrado"

# Paso 2: Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning ".env no encontrado, usando valores por defecto"
fi

# Paso 3: Limpiar contenedores previos
echo ""
echo "Limpiando contenedores previos..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true
print_success "Contenedores previos limpiados"

# Paso 4: Construir imágenes
echo ""
echo "Construyendo imágenes Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

if [ $? -ne 0 ]; then
    print_error "Error al construir imágenes"
    exit 1
fi

print_success "Imágenes construidas exitosamente"

# Paso 5: Levantar contenedores
echo ""
echo "Levantando contenedores en modo detached..."
docker-compose -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    print_error "Error al levantar contenedores"
    exit 1
fi

print_success "Contenedores levantados"

# Paso 6: Esperar a que los servicios base estén listos
echo ""
echo "Esperando 30 segundos para que los servicios inicien..."
sleep 30

# Paso 7: Verificar contenedores críticos
echo ""
echo "=========================================="
echo "🔍 Verificando contenedores críticos"
echo "=========================================="

critical_containers=(
    "cinvestav_postgres"
    "cinvestav_redis"
    "cinvestav_qdrant"
    "cinvestav_nginx"
    "cinvestav_django"
    "cinvestav_api_gateway"
)

all_critical_ok=true

for container in "${critical_containers[@]}"; do
    if ! check_container_status "$container"; then
        all_critical_ok=false
    fi
done

if [ "$all_critical_ok" = false ]; then
    print_error "Algunos contenedores críticos fallaron"
    docker-compose -f docker-compose.prod.yml logs --tail=100
    exit 1
fi

# Paso 8: Ejecutar health checks a endpoints principales
echo ""
echo "=========================================="
echo "🏥 Ejecutando health checks"
echo "=========================================="

services_to_check=(
    "Nginx:cinvestav_nginx:80:/health"
    "Django:cinvestav_django:8000:/health"
    "API Gateway:cinvestav_api_gateway:8100:/health"
    "Auth Service:cinvestav_auth_service:8101:/health"
    "Academic Service:cinvestav_academic_service:8102:/health"
    "Assessment Service:cinvestav_assessment_service:8103:/health"
    "Course Service:cinvestav_course_service:8104:/health"
    "Admin Service:cinvestav_admin_service:8105:/health"
    "Notification Service:cinvestav_notification_service:8106:/health"
    "AI Agent Service:cinvestav_ai_agent_service:8107:/health"
)

all_health_ok=true

for service_info in "${services_to_check[@]}"; do
    IFS=':' read -r name container port endpoint <<< "$service_info"
    if ! check_service_health "$name" "$container" "$port" "$endpoint"; then
        all_health_ok=false
        echo "Logs de $container:"
        docker logs $container --tail 30
    fi
done

# Paso 9: Verificar routing de Nginx
echo ""
echo "=========================================="
echo "🌐 Verificando routing de Nginx"
echo "=========================================="

# Test routing a Django
if curl -f -s "http://localhost/" > /dev/null 2>&1; then
    print_success "Nginx → Django routing funciona"
else
    print_error "Nginx → Django routing falló"
    all_health_ok=false
fi

# Test routing a API Gateway
if curl -f -s "http://localhost/api/" > /dev/null 2>&1; then
    print_success "Nginx → API Gateway routing funciona"
else
    print_error "Nginx → API Gateway routing falló"
    all_health_ok=false
fi

# Paso 10: Resumen final
echo ""
echo "=========================================="
echo "📊 Resumen de la prueba"
echo "=========================================="

if [ "$all_health_ok" = true ]; then
    print_success "✅ TODOS LOS SERVICIOS PASARON LOS HEALTH CHECKS"
    echo ""
    echo "Contenedores corriendo:"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "Para detener los servicios:"
    echo "  docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "Para ver logs en tiempo real:"
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
    exit 0
else
    print_error "❌ ALGUNOS SERVICIOS FALLARON"
    echo ""
    echo "Logs de todos los contenedores:"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    echo ""
    echo "Para investigar más a fondo:"
    echo "  docker-compose -f docker-compose.prod.yml logs <servicio>"
    exit 1
fi
