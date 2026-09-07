#!/usr/bin/env python
import os
import django
import psycopg2
from django.conf import settings

print("🔍 DIAGNÓSTICO BD REMOTA\n")

# Opción 1: Usando Django connection (ya configurado en settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from django.db import connection

def ver_bd_django():
    print("📡 Usando conexión Django configurada en settings:")
    print(f"   Host: {settings.DATABASES['default']['HOST']}")
    print(f"   DB: {settings.DATABASES['default']['NAME']}")
    print(f"   User: {settings.DATABASES['default']['USER']}")
    
    try:
        with connection.cursor() as cursor:
            # Ver tablas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tablas = cursor.fetchall()
            
            print(f"\n📋 Tablas encontradas ({len(tablas)}):")
            for tabla in tablas:
                print(f"   • {tabla[0]}")
                
                # Ver columnas de cada tabla
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position;
                """, [tabla[0]])
                
                columnas = cursor.fetchall()
                print(f"     Columnas: {', '.join([f'{c[0]} ({c[1]})' for c in columnas])}")
                
                # Ver conteo
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]};")
                    count = cursor.fetchone()[0]
                    print(f"     Registros: {count}")
                except:
                    print(f"     Registros: (error al contar)")
                    
            print(f"\n✅ Conexión exitosa a BD remota")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Opción 2: Conexión directa con psycopg2 (si Django falla)
def ver_bd_directa():
    print("\n" + "="*60)
    print("🔄 Intentando conexión directa con psycopg2...")
    
    try:
        conn = psycopg2.connect(
            host="aws-0-us-west-2.pooler.supabase.com",
            port=6543,
            database="postgres",
            user="postgres.ksdemhxapuhtmlgoknqw",
            password="admin_agent2025"
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"   PostgreSQL version: {version[0]}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"   Database: {db_name[0]}")
            
        conn.close()
        print("   ✅ Conexión directa exitosa")
        
    except Exception as e:
        print(f"   ❌ Error conexión directa: {e}")

if __name__ == '__main__':
    ver_bd_django()
    ver_bd_directa() 