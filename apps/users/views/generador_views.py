from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

def index_generador(request):
    """Dashboard del creador de contenido"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'usuario': {
            'nombre': 'Mtro. Ricardo Mendieta',
            'iniciales': 'RM',
            'rol': 'CREADOR SENIOR'
        },
        'estadisticas': {
            'propuestas_activas': 12,
            'validados_usicamm': 8,
            'acreditacion_nacional': 4
        },
        'cursos': [
            {
                'id': 1,
                'titulo': 'La Nueva Escuela Mexicana (NEM)',
                'descripcion': 'Curso obligatorio gratuito. Analiza los principios éticos, la equidad educativa y la revalorización docente.',
                'nivel': 'Educación Básica',
                'tipo_proceso': 'Admisión Obligatoria',
                'estado': 'aceptado',
                'color_estado': 'status-check'
            },
            {
                'id': 2,
                'titulo': 'Competencias Digitales Docentes',
                'descripcion': 'Desarrollo de habilidades tecnológicas para el aula digital y aprendizaje híbrido.',
                'nivel': 'Todos los Niveles',
                'tipo_proceso': 'Formación Continua',
                'estado': 'revision',
                'color_estado': 'status-pending'
            },
            {
                'id': 3,
                'titulo': 'Neurodidáctica en el Aula',
                'descripcion': 'Aplicación de principios neurocientíficos a la enseñanza y el aprendizaje.',
                'nivel': 'Educación Básica',
                'tipo_proceso': 'Especialización',
                'estado': 'observaciones',
                'color_estado': 'status-obs'
            },
            {
                'id': 4,
                'titulo': 'Gestión Escolar Efectiva',
                'descripcion': 'Herramientas administrativas y de liderazgo para directivos y supervisores.',
                'nivel': 'Directivos',
                'tipo_proceso': 'Formación Continua',
                'estado': 'aceptado',
                'color_estado': 'status-check'
            }
        ]
    }
    
    return render(request, 'generador de cursos/index generador de cursos.html', context)

def mis_cursos(request):
    """Repositorio personal de cursos creados"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'usuario': {
            'nombre': 'MTRO. RICARDO MENDIETA',
            'iniciales': 'RM'
        },
        'mis_cursos': [
            {
                'id': 1,
                'titulo': 'Nueva Escuela Mexicana (NEM)',
                'descripcion_corta': 'Estructura validada sobre principios éticos y participación comunitaria.',
                'nivel': 'Educación Básica',
                'estado': 'aceptado',
                'editable': False,
                'color_estado': '#007A7C',
                'texto_estado': 'ACEPTADO',
                'icono_estado': 'fa-check-circle',
                'modulos': [
                    {'titulo': 'Módulo 1: Marco Legal', 'contenido': 'Análisis del Artículo 3° Constitucional y la Ley General de Educación.'},
                    {'titulo': 'Módulo 2: Comunidad', 'contenido': 'Vinculación escuela-comunidad y participación social.'},
                    {'titulo': 'Módulo 3: Equidad', 'contenido': 'Principios de inclusión y equidad educativa.'},
                    {'titulo': 'Módulo 4: Revalorización', 'contenido': 'Reconocimiento y valoración del trabajo docente.'}
                ]
            },
            {
                'id': 2,
                'titulo': 'Competencias Digitales',
                'descripcion_corta': 'Herramientas tecnológicas para la enseñanza híbrida y aprendizaje digital.',
                'nivel': 'Todos los Niveles',
                'estado': 'observaciones',
                'editable': True,
                'color_estado': '#e74c3c',
                'texto_estado': 'OBSERVACIONES',
                'icono_estado': 'fa-exclamation-triangle',
                'modulos': [
                    {'titulo': 'Módulo 1: Plataformas LMS', 'contenido': 'Uso de Moodle, Classroom, Canvas y otras plataformas.'},
                    {'titulo': 'Módulo 2: Herramientas 2.0', 'contenido': 'Aplicación de herramientas web colaborativas.'},
                    {'titulo': 'Módulo 3: Contenido Digital', 'contenido': 'Creación y gestión de materiales educativos digitales.'}
                ]
            },
            {
                'id': 3,
                'titulo': 'Neurodidáctica Aplicada',
                'descripcion_corta': 'Principios neurocientíficos aplicados a la práctica docente cotidiana.',
                'nivel': 'Educación Básica',
                'estado': 'revision',
                'editable': False,
                'color_estado': '#f39c12',
                'texto_estado': 'EN REVISIÓN',
                'icono_estado': 'fa-clock',
                'modulos': [
                    {'titulo': 'Módulo 1: Fundamentos Neurocerebrales', 'contenido': 'Bases del funcionamiento cerebral en el aprendizaje.'},
                    {'titulo': 'Módulo 2: Estrategias Neurodidácticas', 'contenido': 'Técnicas basadas en evidencia neurocientífica.'}
                ]
            },
            {
                'id': 4,
                'titulo': 'Evaluación Auténtica',
                'descripcion_corta': 'Métodos de evaluación centrados en el desempeño y competencias reales.',
                'nivel': 'Todos los Niveles',
                'estado': 'borrador',
                'editable': True,
                'color_estado': '#95a5a6',
                'texto_estado': 'BORRADOR',
                'icono_estado': 'fa-edit',
                'modulos': [
                    {'titulo': 'Módulo 1: Portafolios', 'contenido': 'Diseño e implementación de portafolios de evidencias.'},
                    {'titulo': 'Módulo 2: Rúbricas', 'contenido': 'Construcción y aplicación de rúbricas de evaluación.'}
                ]
            }
        ]
    }
    
    return render(request, 'generador de cursos/mis cursos.html', context)

def perfil_generador(request):
    """Expediente académico SEP"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'perfil': {
            'nombre_completo': 'Dr. Ricardo Mendieta R.',
            'curp': 'MERR850111HDFRRN01',
            'correo': 'r.mendieta@sep.gob.mx',
            'telefono': '+52 55 1234 5678',
            'rol': 'Investigador de Carrera • SEP Federal',
            'foto_perfil': None,
            'verificado': True
        },
        'metricas': {
            'cursos_publicados': 12,
            'diplomados_creados': 4,
            'impacto_docente': '8.4K'
        },
        'documentos': [
            {
                'tipo': 'Cédula Profesional Federal',
                'descripcion': 'Doctorado en Pedagogía • Registro: 8492033',
                'icono': 'fa-id-card',
                'validado': True,
                'entidad': 'SEP Validado'
            },
            {
                'tipo': 'Certificación USICAMM 2025',
                'descripcion': 'Evaluador de Carrera Docente • Folio: 992-IA',
                'icono': 'fa-award',
                'validado': True,
                'entidad': 'SEP Validado'
            },
            {
                'tipo': 'Reconocimiento Internacional',
                'descripcion': 'Investigador Nivel II • Sistema Nacional de Investigadores',
                'icono': 'fa-globe',
                'validado': True,
                'entidad': 'CONACYT Validado'
            },
            {
                'tipo': 'Certificación en Diseño Instruccional',
                'descripcion': 'Especialista en e-learning y diseño de cursos online',
                'icono': 'fa-laptop',
                'validado': True,
                'entidad': 'SEP Validado'
            }
        ]
    }
    
    return render(request, 'generador de cursos/mi perfil.html', context)

def estadisticas_cursos(request):
    """Métricas de impacto del creador"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'usuario': {
            'iniciales': 'RM'
        },
        'estadisticas_generales': {
            'alcance_usuarios': 18240,
            'efectividad_academica': 91.2,
            'calidad_promedio': 4.85
        },
        'datos_graficas': {
            'categorias': {
                'labels': ['NEM Básica', 'C. Digital', 'Directivos', 'Neuroed.'],
                'values': [8200, 6150, 4800, 7300]
            },
            'tendencia_semanal': {
                'labels': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
                'values': [1200, 1900, 1700, 2400]
            }
        },
        'recomendaciones': [
            {
                'id': 1,
                'titulo': 'Propuesta: Introducción a la Estructura Cognitiva',
                'descripcion': 'Dirigido a usuarios con interés en Neurodidáctica pero con tiempos de finalización prolongados en evaluaciones técnicas.',
                'deteccion_ia': 'La tasa de abandono en "Neuroeducación Avanzada" correlaciona con la falta de conceptos básicos en psicología educativa.',
                'sugerencia_ruta': 'Se recomienda enviar este curso base como requisito previo o sugerencia técnica para asegurar la comprensión del tema nacional.',
                'enviada': False
            },
            {
                'id': 2,
                'titulo': 'Propuesta: Gamificación en el Aula',
                'descripcion': 'Para docentes que buscan mejorar la motivación estudiantil pero muestran dificultades en gestión de grupo.',
                'deteccion_ia': 'Los cursos de gestión del aula tienen menor efectividad cuando no se aplican estrategias de motivación.',
                'sugerencia_ruta': 'Integrar elementos de gamificación como complemento a los cursos de gestión existentes.',
                'enviada': True
            },
            {
                'id': 3,
                'titulo': 'Propuesta: Evaluación por Competencias',
                'descripcion': 'Dirigido a directivos y supervisores que necesitan implementar sistemas de evaluación más efectivos.',
                'deteccion_ia': 'Los cursos de gestión escolar muestran mayor impacto cuando se complementan con metodologías de evaluación auténtica.',
                'sugerencia_ruta': 'Crear un módulo transversal sobre evaluación por competencias para todos los cursos de gestión.',
                'enviada': False
            }
        ]
    }
    
    return render(request, 'generador de cursos/estadisticas de cursos.html', context)