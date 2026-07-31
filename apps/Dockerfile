FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY apps/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

# Use Gunicorn with multiple workers for production
CMD ["sh", "-c", "python manage.py collectstatic --noinput --clear && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4 --worker-class gevent --timeout 180 --access-logfile - --error-logfile -"]
