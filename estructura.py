import os
import sys
from io import StringIO
from datetime import datetime

def obtener_estructura_completa(directorio='.', prefijo='', es_ultimo=True, max_nivel=10, nivel=0, ignorar=None):
    """Versión sin límite de líneas - max_nivel más alto"""
    if nivel > max_nivel:
        return
    
    if ignorar is None:
        ignorar = {
            '__pycache__', 'migrations', 'venv', 'env', '.git', 'media',
            '__init__.py', '*.pyc', '*.pyo', 'node_modules',
            'staticfiles', 'mediafiles', '.idea', '.vscode', 'Lib', 'Scripts',
            'Include', 'pyvenv.cfg', '.pytest_cache', '.coverage', 'htmlcov',
            'dist', 'build', '*.egg-info', '.DS_Store'
        }
    
    try:
        items = sorted([i for i in os.listdir(directorio) 
                       if not i.startswith('.') and not any(ign in i for ign in ignorar)])
    except (PermissionError, FileNotFoundError):
        return
    
    for index, item in enumerate(items):
        ruta = os.path.join(directorio, item)
        es_ultimo_item = (index == len(items) - 1)
        
        if es_ultimo:
            prefijo_item = '    ' if nivel > 0 else ''
            conector = '└── '
        else:
            prefijo_item = '│   ' if nivel > 0 else ''
            conector = '├── '
        
        if os.path.isdir(ruta):
            print(f"{prefijo}{prefijo_item}{conector}📁 {item}/")
            nuevo_prefijo = prefijo + ('    ' if es_ultimo_item else '│   ')
            obtener_estructura_completa(ruta, nuevo_prefijo, es_ultimo_item, max_nivel, nivel + 1, ignorar)
        else:
            if item.endswith('.py'):
                icono = '🐍'
            elif item.endswith('.html'):
                icono = '🌐'
            elif item.endswith('.css'):
                icono = '🎨'
            elif item.endswith('.js'):
                icono = '📜'
            elif item.endswith('.json'):
                icono = '📦'
            elif item.endswith('.md'):
                icono = '📝'
            elif item.endswith('.txt'):
                icono = '📄'
            elif item.endswith('.exe'):
                icono = '⚙️'
            elif item.endswith('.yml') or item.endswith('.yaml'):
                icono = '⚙️'
            elif item.endswith('.sql'):
                icono = '🗄️'
            elif item.endswith('.log'):
                icono = '📋'
            elif item.endswith('.bat'):
                icono = '⚙️'
            elif item.endswith('.ps1'):
                icono = '⚙️'
            else:
                icono = '📄'
            print(f"{prefijo}{prefijo_item}{conector}{icono} {item}")

def mostrar_todo():
    """Muestra TODAS las líneas sin límite"""
    print("🔍 Generando estructura COMPLETA del proyecto...\n")
    
    # Redirigir salida
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    # Obtener el directorio raíz
    directorio_raiz = os.path.dirname(os.path.abspath(__file__))
    print(f"📂 Directorio raíz: {directorio_raiz}\n")
    print("=" * 80 + "\n")
    
    # Ejecutar con un nivel alto para capturar todo
    obtener_estructura_completa('.', max_nivel=10)
    
    # Obtener la salida
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    # Contar líneas
    lineas = output.count('\n') + 1
    
    print(f"\n📊 Total de líneas generadas: {lineas}")
    print("=" * 80)
    print("ESTRUCTURA COMPLETA:")
    print("=" * 80)
    
    # MOSTRAR TODO SIN LÍMITE
    print(output)
    
    print("=" * 80)
    print(f"✅ Total de líneas mostradas: {lineas}")
    
    # Preguntar si quiere guardar el archivo
    respuesta = input("\n❓ ¿Quieres guardar esta estructura en un archivo? (s/n): ")
    if respuesta.lower() == 's':
        nombre_archivo = 'estructura_completa.txt'
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ESTRUCTURA COMPLETA DEL PROYECTO\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Directorio raíz: {directorio_raiz}\n")
            f.write(f"Total de líneas: {lineas}\n")
            f.write("=" * 80 + "\n\n")
            f.write(output)
        
        print(f"\n✅ Archivo '{nombre_archivo}' guardado en: {os.path.abspath(nombre_archivo)}")
        print(f"📦 Tamaño del archivo: {os.path.getsize(nombre_archivo) / 1024:.2f} KB")

if __name__ == "__main__":
    try:
        mostrar_todo()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        input("\nPresiona Enter para salir...")