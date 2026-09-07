from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.users.services.permisos import requiere_rol
from apps.users.config.constants import ROLE_GENERADOR
from apps.users.services.vistas_bd_service import VistasBdService
from apps.users.services.curso_service import CursoService
import json
import re
from html import escape
import logging

logger = logging.getLogger(__name__)

# Lista blanca de modificaciones HTML permitidas por la IA
MODIFICACIONES_PERMITIDAS = {
    'texto_contenido': r'^[a-zA-Z0-9\s\.,;:!?\'\"\-\n\r]+$',
    'encabezados_h1_h6': r'^[a-zA-Z0-9\s\.,;:!?\'\"\-\n\r]+$',
    'listas_ul_ol': r'^[a-zA-Z0-9\s\.,;:!?\'\"\-\n\r]+$',
    'parrafos': r'^[a-zA-Z0-9\s\.,;:!?\'\"\-\n\r]+$',
    'clases_css_visuales': r'^[a-zA-Z0-9\-_\s]+$',
    'atributos_data_seguros': r'^[a-zA-Z0-9\-_\s:]+$',
}

# Lista negra estricta - cosas que NO puede hacer la IA
PROHIBICIONES_ESTRICTAS = [
    r'script', r'onclick', r'onload', r'onerror', r'onmouseover',
    r'javascript:', r'eval\(', r'Function\(', r'setTimeout\(',
    r'setInterval\(', r'document\.write', r'innerHTML.*<script',
    r'document\.cookie', r'localStorage', r'sessionStorage',
    r'window\.location', r'window\.top', r'window\.parent',
    r'iframe', r'embed', r'object', r'form', r'input', r'button',
    r'CREATE', r'INSERT', r'UPDATE', r'DELETE', r'DROP', r'ALTER',
    r'exec\(', r'system\(', r'shell_exec', r'passthru\(',
    r'__import__', r'import os', r'import sys', r'subprocess',
    r'eval\s*\(', r'exec\s*\(', r'compile\s*\(',
]

# Lista negra estricta - cosas que NO puede hacer la IA
PROHIBICIONES_ESTRICTAS = [
    'script', 'onclick', 'onload', 'onerror', 'onmouseover',
    'javascript:', 'eval(', 'Function(', 'setTimeout(',
    'setInterval(', 'document.write', 'innerHTML.*<script',
    'document.cookie', 'localStorage', 'sessionStorage',
    'window.location', 'window.top', 'window.parent',
    'iframe', 'embed', 'object', 'form', 'input', 'button',
    'CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER',
    'exec(', 'system(', 'shell_exec', 'passthru(',
    '__import__', 'import os', 'import sys', 'subprocess',
    'eval\\s*\\(', 'exec\\s*\\(', 'compile\\s*\\(',
]

class SanitizadorHTMLSeguro:
    """Clase para sanitizar modificaciones HTML de la IA con restricciones de seguridad"""
    
    @staticmethod
    def es_modificacion_segura(modificacion):
        """Verifica si una modificación está en la lista blanca"""
        for tipo, patron in MODIFICACIONES_PERMITIDAS.items():
            if re.match(patron, modificacion, re.IGNORECASE):
                return True, tipo
        return False, None
    
    @staticmethod
    def contiene_prohibiciones(texto):
        """Verifica si el texto contiene comandos prohibidos"""
        for prohibido in PROHIBICIONES_ESTRICTAS:
            try:
                if re.search(prohibido, texto, re.IGNORECASE):
                    return True, prohibido
            except re.error:
                # Si el regex es inválido, lo ignoramos
                continue
        return False, None
    
    @staticmethod
    def sanitizar_modificacion(tipo, contenido, elemento_id):
        """Sanitiza una modificación según su tipo"""
        if tipo == 'texto_contenido':
            # Solo permite texto plano sin HTML
            return {
                'tipo': 'texto',
                'elemento_id': elemento_id,
                'contenido': escape(contenido),
                'html_seguro': escape(contenido).replace('\n', '<br>')
            }
        elif tipo == 'encabezados_h1_h6':
            # Permite encabezados simples
            if re.match(r'^[h1-h6]$', elemento_id, re.IGNORECASE):
                return {
                    'tipo': 'encabezado',
                    'elemento_id': elemento_id,
                    'contenido': escape(contenido),
                    'html_seguro': f'<{elemento_id}>{escape(contenido)}</{elemento_id}>'
                }
        elif tipo == 'clases_css_visuales':
            # Solo permite clases CSS seguras
            clases = re.findall(r'[a-zA-Z0-9\-_]+', contenido)
            return {
                'tipo': 'clase_css',
                'elemento_id': elemento_id,
                'contenido': ' '.join(clases),
                'html_seguro': f' class="{" ".join(clases)}"'
            }
        
        return None

@csrf_exempt
def modificar_html_seguro(request):
    """
    Endpoint seguro para que la IA modifique HTML del generador
    con restricciones estrictas de seguridad
    """
    logger.info(f"modificar_html_seguro llamado: {request.method}, body: {request.body[:200]}")
    
    try:
        if request.method == "GET":
            return JsonResponse({
                'success': True,
                'mensaje': 'Endpoint disponible para pruebas GET'
            })
            
        datos = json.loads(request.body)
        
        # Validar campos requeridos
        if 'modificacion' not in datos or 'elemento_id' not in datos:
            return JsonResponse({
                'success': False,
                'error': 'Faltan campos requeridos: modificacion y elemento_id'
            }, status=400)
        
        modificacion = datos['modificacion']
        elemento_id = datos['elemento_id']
        
        # Verificar prohibiciones estrictas
        tiene_prohibicion, prohibicion = SanitizadorHTMLSeguro.contiene_prohibiciones(modificacion)
        if tiene_prohibicion:
            return JsonResponse({
                'success': False,
                'error': f'Modificación no permitida por seguridad: {prohibicion}',
                'razon': 'Intento de ejecutar código peligroso o modificar estructura del sistema'
            }, status=403)
        
        # Verificar si la modificación está en la lista blanca
        es_segura, tipo_modificacion = SanitizadorHTMLSeguro.es_modificacion_segura(modificacion)
        if not es_segura:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de modificación no permitida',
                'razon': 'Solo se permiten modificaciones de texto, encabezados y estilos visuales'
            }, status=403)
        
        # Sanitizar la modificación
        resultado = SanitizadorHTMLSeguro.sanitizar_modificacion(
            tipo_modificacion, 
            modificacion, 
            elemento_id
        )
        
        if resultado is None:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo procesar la modificación de forma segura'
            }, status=400)
        
        # Verificar que el elemento_id existe en la lista blanca de elementos DOM permitidos
        elementos_dom_permitidos = [
            'cont-bloque1', 'cont-bloque2', 'cont-bloque3', 'cont-bloque4',
            'quiz-final', 'chat-box', 'user-input',
            'titulo-curso', 'descripcion-curso',
            'objetivos-container', 'competencias-container',
            'bibliografia-container', 'evaluacion-container'
        ]
        
        if elemento_id not in elementos_dom_permitidos:
            return JsonResponse({
                'success': False,
                'error': 'Elemento DOM no permitido para modificación',
                'razon': 'Solo se pueden modificar elementos de contenido del curso, no estructura del sistema'
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Modificación aplicada de forma segura',
            'modificacion': resultado
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)

@requiere_rol(ROLE_GENERADOR)
def generador_de_cursos(request, curso_id=None):
    context = VistasBdService.contexto_generador(request)
    if curso_id is not None:
        context['curso_id'] = curso_id
    
    # Agregar timestamp para evitar caché del navegador
    import time
    context['cache_buster'] = int(time.time())
    
    return render(request, 'generador_cursos/generador_de_cursos.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@requiere_rol(ROLE_GENERADOR)
def guardar_curso_generado(request):
    """Guardar curso generado por IA"""
    try:
        datos = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        curso = CursoService.crear_curso(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion', ''),
            docente_id=usuario_id,
            estado='Borrador',
            generado_con_ia=True
        )
        
        if 'contenido' in datos:
            curso.contenido_json = datos['contenido']
            curso.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Curso generado guardado exitosamente',
            'curso_id': curso.id_curso
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)