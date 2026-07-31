#!/bin/bash

# Script de despliegue automatizado para producción
# CinvestavUsicamm Backend

set -e

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Función para verificar si estamos en el directorio correcto
check_directory() {
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_error "No se encontró docker-compose.prod.yml. Asegúrate de estar en el directorio raíz del proyecto."
        exit 1
    fi
    print_success "Directorio del proyecto verificado"
}

# Función para verificar permisos de Docker
check_docker_permissions() {
    if ! docker ps > /dev/null 2>&1; then
        print_error "No tienes permisos para ejecutar Docker. Ejecuta: sudo usermod -aG docker $USER"
        exit 1
    fi
    print_success "Permisos de Docker verificados"
}

# Función para hacer backup de la base de datos
backup_database() {
    print_info "Creando backup de la base de datos..."
    
    BACKUP_DIR="./backups"
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p $BACKUP_DIR
    
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ${POSTGRES_USER:-user} ${POSTGRES_DB:-cinvestav_db} > $BACKUP_FILE 2>/dev/null; then
        print_success "Backup creado: $BACKUP_FILE"
        
        # Mantener solo los últimos 7 backups
        ls -t $BACKUP_DIR/db_backup_*.sql | tail -n +8 | xargs -r rm --
        print_info "Backups antiguos limpiados (manteniendo últimos 7)"
    else
        print_warning "No se pudo crear el backup (puede ser que el contenedor no esté corriendo)"
    fi
}

# Función para limpiar imágenes huérfanas
cleanup_docker_images() {
    print_info "Limpiando imágenes Docker huérfanas..."
    
    # Eliminar contenedores detenidos
    docker container prune -f > /dev/null 2>&1
    
    # Eliminar imágenes no utilizadas (dangling)
    docker image prune -f > /dev/null 2>&1
    
    # Eliminar volúmenes no utilizados
    docker volume prune -f > /dev/null 2>&1
    
    # Mostrar espacio liberado
    SPACE_SAVED=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Reclaimable}}")
    print_success "Limpieza completada"
    echo "$SPACE_SAVED"
}

# Función para actualizar el código desde git
update_code() {
    print_info "Actualizando código desde Git..."
    
    # Verificar si estamos en un repo git
    if [ -d ".git" ]; then
        # Guardar cambios locales no commitidos
        git stash push -m "Auto-stash before deploy $(date)" || true
        
        # Pull de cambios
        git pull origin $(git branch --show-current)
        
        print_success "Código actualizado desde Git"
    else
        print_warning "No es un repositorio Git, omitiendo actualización"
    fi
}

# Función para construir y levantar contenedores
deploy_containers() {
    print_info "Construyendo imágenes Docker..."
    
    # Construir sin caché para asegurar cambios
    docker-compose -f docker-compose.prod.yml build --no-cache --parallel
    
    if [ $? -ne 0 ]; then
        print_error "Error al construir imágenes"
        exit 1
    fi
    
    print_success "Imágenes construidas exitosamente"
    
    print_info "Levantando contenedores en modo detached..."
    
    # Levantar contenedores
    docker-compose -f docker-compose.prod.yml up -d
    
    if [ $? -ne 0 ]; then
        print_error "Error al levantar contenedores"
        exit 1
    fi
    
    print_success "Contenedores levantados"
}

# Función para ejecutar migraciones de Django
run_migrations() {
    print_info "Ejecutando migraciones de Django..."
    
    # Esperar a que Django esté listo
    sleep 10
    
    docker-compose -f docker-compose.prod.yml exec -T django python manage.py migrate --noinput
    
    if [ $? -ne 0 ]; then
        print_warning "Error al ejecutar migraciones (puede ser que ya estén aplicadas)"
    else
        print_success "Migraciones ejecutadas"
    fi
}

# Función para recolectar archivos estáticos
collect_static() {
    print_info "Recolectando archivos estáticos..."
    
    docker-compose -f docker-compose.prod.yml exec -T django python manage.py collectstatic --noinput --clear
    
    if [ $? -ne 0 ]; then
        print_warning "Error al recolectar estáticos (puede ser que ya estén recolectados)"
    else
        print_success "Archivos estáticos recolectados"
    fi
}

# Función para verificar health checks
verify_deployment() {
    print_info "Verificando health checks de servicios críticos..."
    
    local max_attempts=30
    local attempt=1
    local services_healthy=true
    
    # Lista de servicios críticos a verificar
    declare -A services=(
        ["nginx"]="http://localhost:80/health"
        ["django"]="http://localhost:8000/health"
        ["api_gateway"]="http://localhost:8100/health"
    )
    
    for service in "${!services[@]}"; do
        local endpoint="${services[$service]}"
        local healthy=false
        
        echo "Verificando $service..."
        
        for ((attempt=1; attempt<=max_attempts; attempt++)); do
            if curl -f -s "$endpoint" > /dev/null 2>&1; then
                print_success "$service está saludable"
                healthy=true
                break
            fi
            echo "  Intento $attempt/$max_attempts: $service no responde..."
            sleep 2
        done
        
        if [ "$healthy" = false ]; then
            print_error "$service no pasó el health check"
            services_healthy=false
        fi
    done
    
    if [ "$services_healthy" = false ]; then
        print_error "Algunos servicios críticos no están saludables"
        print_info "Verificando logs de contenedores con problemas..."
        docker-compose -f docker-compose.prod.yml logs --tail=50
        return 1
    fi
    
    print_success "Todos los servicios críticos están saludables"
    return 0
}

# Función para mostrar resumen del despliegue
show_deployment_summary() {
    echo ""
    echo "=========================================="
    echo "📊 Resumen del Despliegue"
    echo "=========================================="
    
    echo "Contenedores corriendo:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "Uso de recursos:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    echo ""
    print_success "Despliegue completado exitosamente"
    echo ""
    echo "Comandos útiles:"
    echo "  Ver logs en tiempo real: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  Detener servicios: docker-compose -f docker-compose.prod.yml down"
    echo "  Reiniciar servicio: docker-compose -f docker-compose.prod.yml restart <servicio>"
}

# Función para rollback en caso de error
rollback_deployment() {
    print_error "Iniciando rollback..."
    
    # Restaurar stash de git si existe
    if [ -d ".git" ]; then
        git stash pop || true
    fi
    
    # Levantar versión anterior
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    
    print_warning "Rollback completado. Verifica el estado de los servicios."
}

# Main execution
main() {
    echo "=========================================="
    echo "🚀 Script de Despliegue - CinvestavUsicamm"
    echo "=========================================="
    echo "Fecha: $(date)"
    echo ""
    
    # Verificar si se debe hacer backup
    DO_BACKUP=true
    SKIP_UPDATE=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-backup)
                DO_BACKUP=false
                shift
                ;;
            --skip-update)
                SKIP_UPDATE=true
                shift
                ;;
            --help)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --no-backup      No crear backup de base de datos"
                echo "  --skip-update    No actualizar código desde Git"
                echo "  --help           Mostrar esta ayuda"
                exit 0
                ;;
            *)
                print_error "Opción desconocida: $1"
                exit 1
                ;;
        esac
    done
    
    # Ejecutar pasos del despliegue
    check_directory
    check_docker_permissions
    
    if [ "$DO_BACKUP" = true ]; then
        backup_database
    fi
    
    if [ "$SKIP_UPDATE" = false ]; then
        update_code
    fi
    
    deploy_containers
    run_migrations
    collect_static
    
    if verify_deployment; then
        cleanup_docker_images
        show_deployment_summary
        exit 0
    else
        print_error "Despliegue falló. Iniciando rollback..."
        rollback_deployment
        exit 1
    fi
}

# Capturar errores y hacer rollback
trap 'print_error "Error durante el despliegue"; rollback_deployment; exit 1' ERR

# Ejecutar main con todos los argumentos
main "$@"
