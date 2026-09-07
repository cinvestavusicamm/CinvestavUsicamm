# Deployment Guide - EscalafonIA Jaguar

## Overview

This guide provides comprehensive instructions for deploying the EscalafonIA Jaguar system to production using Docker and Docker Compose.

## Prerequisites

### Software Requirements

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **Text Editor**: For editing configuration files
- **SSL Certificate**: For HTTPS (recommended for production)

### Hardware Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- Network: 100 Mbps

**Recommended**:
- CPU: 8 cores
- RAM: 16 GB
- Disk: 100 GB SSD
- Network: 1 Gbps

---

## Pre-Deployment Checklist

### 1. Security Configuration

Before deploying to production, ensure the following security measures are in place:

#### Update `.env` File

```env
# Django Settings
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/escalafon_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Microservices URLs
VALIDATION_SERVICE_URL=http://django:8000
BACKEND_API_URL=http://backend:8003
MICROSERVICE_DB_URL=http://db:5432
DJANGO_BACKEND_URL=http://django:8000

# Security
MICROSERVICE_SECRET=<generate-strong-secret-key>
POSTGRES_PASSWORD=<generate-strong-password>
```

**Generate Strong Secrets**:

```bash
# Generate Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate MICROSERVICE_SECRET
openssl rand -hex 32
```

#### Enable SSL/HTTPS

In `core/settings/base.py`:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Database Configuration

#### Production Database

Update the database URL in `.env`:

```env
DATABASE_URL=postgresql://production_user:strong_password@production-db-host:5432/escalafon_db
```

#### Update docker-compose.yml

```yaml
db:
  environment:
    POSTGRES_USER: production_user
    POSTGRES_PASSWORD: strong_password
    POSTGRES_DB: escalafon_db
```

### 3. Domain Configuration

#### Configure DNS

- Point your domain to the server IP address
- Create A records:
  - `@` → Server IP
  - `www` → Server IP
  - `api` → Server IP (optional)

#### Configure Allowed Hosts

```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Deployment Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd CinvestavUsicamm
```

### Step 2: Configure Environment Variables

```bash
cd infrastructure
cp ../.env.example ../.env
nano ../.env
```

Edit the `.env` file with production values.

### Step 3: Build Docker Images

```bash
docker-compose build
```

This will build images for:
- Django backend
- FastAPI backend
- MS Orchestrator

### Step 4: Start Services

```bash
docker-compose up -d
```

This will start all services in detached mode:
- PostgreSQL database
- Ollama AI engine
- FastAPI backend
- Django backend
- MS Orchestrator

### Step 5: Run Database Migrations

```bash
docker-compose exec django python manage.py migrate
```

### Step 6: Collect Static Files

```bash
docker-compose exec django python manage.py collectstatic --noinput
```

### Step 7: Create Superuser

```bash
docker-compose exec django python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 8: Verify Deployment

Check that all services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS              PORTS
escalafon_db          Up (healthy)        0.0.0.0:5432->5432/tcp
motor_ollama          Up (running)         0.0.0.0:11434->11434/tcp
ia_service_core       Up (healthy)        0.0.0.0:8003->8003/tcp
escalafon_django      Up (running)         0.0.0.0:8001->8000/tcp
escalafon_orchestrator Up (running)         0.0.0.0:9000->9000/tcp
```

Test health checks:

```bash
# Django health check
curl http://localhost:8001/health/

# FastAPI health check
curl http://localhost:8003/health

# Orchestrator health check
curl http://localhost:9000/health
```

---

## SSL/HTTPS Configuration

### Option 1: Using Nginx Reverse Proxy (Recommended)

#### Install Nginx

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

#### Configure Nginx

Create `/etc/nginx/sites-available/escalafonia`:

```nginx
upstream django_backend {
    server localhost:8001;
}

upstream fastapi_backend {
    server localhost:8003;
}

upstream orchestrator {
    server localhost:9000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ai/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /orchestrator/ {
        proxy_pass http://orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/escalafonia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Obtain SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically configure SSL and redirect HTTP to HTTPS.

### Option 2: Using Traefik

Add Traefik to docker-compose.yml:

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your@email.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt
    networks:
      - escalafon_net

  django:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.django.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.django.entrypoints=websecure"
      - "traefik.http.routers.django.tls.certresolver=myresolver"
      - "traefik.http.services.django.loadbalancer.server.port=8000"
```

---

## Database Management

### Backups

#### Manual Backup

```bash
docker-compose exec db pg_dump -U user escalafon_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Automated Backup

Create a cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * docker-compose exec db pg_dump -U user escalafon_db > /backups/backup_$(date +\%Y\%m\%d).sql
```

#### Restore from Backup

```bash
docker-compose exec -T db psql -U user escalafon_db < backup_20240101_020000.sql
```

### Database Migration Strategy

Since models use `managed = False`:

1. **Schema Changes**: Apply directly to production database
2. **Model Updates**: Update Django models to match schema
3. **Generate Migrations**: For reference only
4. **Test**: Test changes in staging first

```bash
# Generate migration (for reference)
docker-compose exec django python manage.py makemigrations

# Do NOT run migrate in production for managed=False models
# docker-compose exec django python manage.py migrate
```

---

## Monitoring and Logging

### View Logs

#### All Services

```bash
docker-compose logs -f
```

#### Specific Service

```bash
# Django logs
docker-compose logs -f django

# FastAPI logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f db

# Ollama logs
docker-compose logs -f ollama

# Orchestrator logs
docker-compose logs -f ms_orchestrator
```

#### Application Logs

```bash
# Error logs
tail -f logs/error.log

# Security logs
tail -f logs/security.log
```

### Log Rotation

Configure logrotate for application logs:

Create `/etc/logrotate.d/escalafonia`:

```
/path/to/CinvestavUsicamm/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

---

## Performance Tuning

### Django Configuration

#### Gunicorn Workers

In `infrastructure/docker-compose.yml`:

```yaml
django:
  command: >
    sh -c "python manage.py collectstatic --noinput &&
          python manage.py migrate &&
          gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 180 --worker-class gevent --workers 4"
```

Adjust `--workers` based on CPU cores (2x CPU cores is a good starting point).

#### Database Connection Pooling

In `core/settings/base.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'escalafon_db',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'db',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### PostgreSQL Configuration

#### Increase Shared Buffers

In PostgreSQL configuration:

```sql
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

Restart database:

```bash
docker-compose restart db
```

---

## Scaling Strategies

### Horizontal Scaling

#### Multiple Django Instances

```yaml
django:
  deploy:
    replicas: 3
  # ... rest of configuration
```

#### Load Balancer

Use Nginx or HAProxy to distribute traffic:

```nginx
upstream django_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}
```

### Vertical Scaling

#### Increase Resources

```yaml
django:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

---

## Health Checks

### Docker Health Checks

All services have health checks configured:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user -d escalafon_db"]
  interval: 5s
  timeout: 5s
  retries: 5
```

### External Monitoring

Use tools like:
- **Uptime Robot**: Monitor HTTP endpoints
- **Prometheus + Grafana**: Metrics and dashboards
- **Datadog**: Full-stack monitoring
- **Sentry**: Error tracking

---

## Troubleshooting

### Service Won't Start

#### Check Logs

```bash
docker-compose logs <service_name>
```

#### Check Dependencies

```bash
docker-compose ps
```

Ensure all dependencies are healthy before starting dependent services.

#### Common Issues

1. **Database Connection Failed**
   - Verify database is healthy
   - Check DATABASE_URL in .env
   - Ensure network connectivity

2. **Port Already in Use**
   ```bash
   sudo lsof -i :8001
   sudo kill -9 <PID>
   ```

3. **Permission Denied**
   ```bash
   sudo chown -R $USER:$USER .
   ```

### High Memory Usage

#### Check Container Memory

```bash
docker stats
```

#### Solutions

1. Reduce worker count
2. Increase server RAM
3. Implement caching
4. Optimize database queries

### Slow Response Times

#### Check Database Performance

```bash
docker-compose exec db psql -U user -d escalafon_db -c "SELECT * FROM pg_stat_activity;"
```

#### Solutions

1. Add database indexes
2. Optimize queries
3. Enable query caching
4. Scale horizontally

---

## Rollback Procedure

### Quick Rollback

```bash
# Stop current deployment
docker-compose down

# Switch to previous version
git checkout <previous-commit>

# Rebuild and start
docker-compose up --build -d

# Run migrations if needed
docker-compose exec django python manage.py migrate
```

### Database Rollback

```bash
# Restore from backup
docker-compose exec -T db psql -U user escalafon_db < backup_20240101_020000.sql
```

---

## Maintenance Mode

### Enable Maintenance Mode

Create a maintenance page and configure Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /var/www/maintenance;
        index maintenance.html;
    }
}
```

### Disable Maintenance Mode

Remove or comment out the maintenance configuration and reload Nginx.

---

## Security Hardening

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Docker
sudo ufw allow 2375/tcp

# Enable firewall
sudo ufw enable
```

### Fail2Ban Configuration

Install and configure Fail2Ban:

```bash
sudo apt install fail2ban
```

Create `/etc/fail2ban/jail.local`:

```ini
[django]
enabled = true
port = http,https
filter = django
logpath = /path/to/CinvestavUsicamm/logs/security.log
maxretry = 5
bantime = 3600
```

### Regular Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

---

## Disaster Recovery

### Backup Strategy

1. **Daily**: Automated database backups
2. **Weekly**: Full system backup (including volumes)
3. **Monthly**: Off-site backup storage

### Recovery Procedure

1. Restore database from backup
2. Restore application code from Git
3. Rebuild Docker images
4. Start services
5. Verify functionality

---

## CI/CD Pipeline (Future)

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/CinvestavUsicamm
            git pull
            docker-compose down
            docker-compose up --build -d
            docker-compose exec django python manage.py migrate
            docker-compose exec django python manage.py collectstatic --noinput
```

---

## Production Checklist

- [ ] Update `.env` with production values
- [ ] Generate strong secrets
- [ ] Configure SSL/HTTPS
- [ ] Set up domain DNS
- [ ] Configure firewall
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Set up monitoring
- [ ] Test health checks
- [ ] Test rollback procedure
- [ ] Document recovery procedures
- [ ] Train team on deployment process

---

## Support and Maintenance

### Regular Tasks

**Daily**:
- Check service health
- Review error logs
- Monitor resource usage

**Weekly**:
- Review security logs
- Check backup integrity
- Update dependencies

**Monthly**:
- Review and update documentation
- Performance audit
- Security audit

### Emergency Contacts

- System Administrator: [contact]
- Database Administrator: [contact]
- Development Team: [contact]

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Ollama Documentation](https://ollama.ai/docs)
