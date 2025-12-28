import os
import sys
import django

# 1️⃣ Agregar la raíz del proyecto al PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 2️⃣ Configurar settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

# 3️⃣ Inicializar Django
django.setup()

# 4️⃣ Test de conexión
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print("Resultado BD:", result)
