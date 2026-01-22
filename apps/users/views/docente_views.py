from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

def panel_docente(request):
    """Dashboard principal del docente"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    # Verificar rol
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('dashboard')
    
    context = {
        'docente': {
            'nombre_completo': request.session.get('usuario_nombre', 'Docente'),
            'curp': 'PEEX840512MDF',
            'numero_empleado': 'SEP-774402',
            'ciclo_escolar': '2025-2026',
            'rol': 'Docente',
        },
        'estadisticas': {
            'antiguedad': '12 Años',
            'nivel_carrera': 'Carrera Mag. E',
            'incentivo': '35% (K1)',
            'entidad': 'CDMX',
        },
        'evaluaciones_pendientes': [
            {
                'titulo': 'Valoración de Aptitudes (NEM 2026)',
                'descripcion': 'Evaluación diagnóstica obligatoria para promoción.',
                'tipo_accion': 'iniciar',
                'url_accion': '#',
            }
        ],
        'progreso_rutas': {
            'eje': 'Inclusión en el Aula',
            'porcentaje': 85,
        },
        'recomendacion_ia': {
            'titulo': 'Sugerencia de Formación',
            'mensaje': 'Elena, tras analizar tu perfil, te recomendamos fortalecer competencias en equidad educativa para mejorar tu puntaje en la próxima evaluación.',
            'curso_sugerido': 'Estrategias de Equidad',
            'url_inscripcion': '#',
        },
        'estatus_promocion': {
            'folio': '#MX-2026-99',
            'estado': 'Validación de Portafolio en Proceso',
            'porcentaje': 60,
        }
    }
    
    return render(request, 'panel docente.html', context)

def index_docente(request):
    """Página de bienvenida y guía técnica"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('dashboard')
    
    context = {
        'sistema_info': {
            'nombre_sistema': 'ESCALAFONIA',
            'titulo_bienvenida': 'Gestión de Talento',
            'descripcion_ia': 'Asistente Jaguar IA',
        },
        'catalogo_cursos': [
            {
                'titulo': 'Catálogo de Cursos',
                'descripcion': 'Explora la oferta educativa oficial...',
                'icono': 'fas fa-book-open',
            },
            {
                'titulo': 'Promociones',
                'descripcion': 'Procesos de promoción horizontal y vertical...',
                'icono': 'fas fa-chart-line',
            },
            {
                'titulo': 'Consultar Progreso',
                'descripcion': 'Portafolio digital de evidencias...',
                'icono': 'fas fa-tasks',
            },
            {
                'titulo': 'Foros',
                'descripcion': 'Colabora con la comunidad docente...',
                'icono': 'fas fa-comments',
            },
        ],
        'guia_pasos': [
            {
                'numero': 1,
                'titulo': 'Perfil',
                'descripcion': 'Consulta tu información personal',
                'icono': 'fas fa-user',
            },
            {
                'numero': 2,
                'titulo': 'Carga PDF',
                'descripcion': 'Sube tus documentos',
                'icono': 'fas fa-file-pdf',
            },
            {
                'numero': 3,
                'titulo': 'Valida',
                'descripcion': 'Espera la validación oficial',
                'icono': 'fas fa-check-circle',
            },
            {
                'numero': 4,
                'titulo': 'Monitorea',
                'descripcion': 'Seguimiento en tiempo real',
                'icono': 'fas fa-chart-bar',
            },
        ]
    }
    
    return render(request, 'index docente.html', context)

def perfil_docente(request):
    """Consulta de perfil propio (solo lectura)"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    if request.session.get('usuario_rol') != 'Docente':
        return redirect('dashboard')
    
    context = {
        'docente': {
            'nombre_completo': request.session.get('usuario_nombre', 'Docente'),
            'curp': 'PEEX840512MDF',
            'puesto': 'Docente de Educación Primaria',
            'numero_empleado': 'SEP-774402',
            'foto_url': None,
        },
        'informacion_laboral': {
            'antiguedad_sistematica': '12 Años, 4 Meses',
            'nivel_carrera_magisterial': 'Nivel E (Consolidado)',
            'centro_trabajo': {
                'cct': '09DPR1234Z - Sector 04',
                'nombre': 'Escuela Primaria Ejemplo',
            },
            'ultima_sincronizacion': '08/01/2026',
            'verificacion_sep': True,
        },
        'estatus_promocion': {
            'incentivo_actual': '35% (K1)',
            'proxima_evaluacion': 'Marzo 2026',
        },
        'insights_ia': {
            'resumen': 'Maestra Elena, su perfil es idóneo para la convocatoria de Promoción 2026. Su experiencia en inclusión educativa y su formación continua le posicionan favorablemente.',
            'sugerencia': 'le sugerimos completar 20 horas adicionales de formación en competencias digitales para maximizar sus posibilidades de promoción.',
            'modelo_ia': 'Llama 3.1',
        }
    }
    
    return render(request, 'Perfil docente.html', context)