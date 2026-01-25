from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
import json

def dashboard_evaluador(request):
    """Panel principal del evaluador con estadísticas"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'stats_evaluaciones_pendientes': 3,
        'stats_preguntas_pendientes': 48,
        'stats_evaluaciones_programadas': 15,
        'stats_preguntas_banco': 12,
        'actividad_reciente': [
            {
                'tipo': 'evaluacion',
                'titulo': 'Evaluación Matemáticas',
                'descripcion': 'Evaluación completa',
                'fecha_hace': 'Hace 2 horas',
                'icono': 'fa-robot'
            },
            {
                'tipo': 'validacion',
                'titulo': 'Validación de Preguntas',
                'descripcion': '15 preguntas aprobadas',
                'fecha_hace': 'Hace 4 horas',
                'icono': 'fa-check'
            },
            {
                'tipo': 'generacion',
                'titulo': 'Generación IA',
                'descripcion': '10 preguntas generadas',
                'fecha_hace': 'Hace 6 horas',
                'icono': 'fa-magic'
            }
        ]
    }
    
    return render(request, 'Evaluador/dashboard.html', context)

def banco_preguntas(request):
    """Gestión del repositorio de preguntas con filtros y paginación"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    # Datos simulados para el banco de preguntas
    preguntas_simuladas = [
        {
            'id': 1,
            'enunciado': '¿Cuál de las siguientes estrategias es más efectiva para enseñar fracciones a estudiantes de primaria?',
            'asignatura': 'matematicas',
            'asignatura_label': 'Matemáticas',
            'nivel': 'primaria',
            'dimension': 'pedagogica',
            'tipo': 'opcion_multiple',
            'tipo_label': 'Opción Múltiple',
            'estado': 'validada',
            'estado_label': 'Validada',
            'fecha_creacion': '15/06/2024',
            'dificultad': 'Media',
            'nivel_bloom': 'Aplicar',
            'editable': True,
            'validable': False
        },
        {
            'id': 2,
            'enunciado': '¿Qué principio pedagógico de la Nueva Escuela Mexicana prioriza el aprendizaje basado en proyectos?',
            'asignatura': 'espanol',
            'asignatura_label': 'Español',
            'nivel': 'secundaria',
            'dimension': 'pedagogica',
            'tipo': 'opcion_multiple',
            'tipo_label': 'Opción Múltiple',
            'estado': 'pendiente',
            'estado_label': 'Pendiente',
            'fecha_creacion': '16/06/2024',
            'dificultad': 'Alta',
            'nivel_bloom': 'Analizar',
            'editable': True,
            'validable': True
        },
        {
            'id': 3,
            'enunciado': 'La evaluación formativa se caracteriza por:',
            'asignatura': 'ciencias',
            'asignatura_label': 'Ciencias',
            'nivel': 'primaria',
            'dimension': 'didactica',
            'tipo': 'opcion_multiple',
            'tipo_label': 'Opción Múltiple',
            'estado': 'rechazada',
            'estado_label': 'Rechazada',
            'fecha_creacion': '14/06/2024',
            'dificultad': 'Baja',
            'nivel_bloom': 'Comprender',
            'editable': False,
            'validable': False
        }
    ] * 8  # Simular 24 preguntas
    
    paginator = Paginator(preguntas_simuladas, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_preguntas': 1247,
        'preguntas_validadas': 1189,
        'preguntas_pendientes': 48,
        'preguntas_rechazadas': 10,
        
        # Opciones para filtros
        'niveles_educativos': [
            {'value': 'preescolar', 'label': 'Preescolar'},
            {'value': 'primaria', 'label': 'Primaria'},
            {'value': 'secundaria', 'label': 'Secundaria'},
        ],
        'asignaturas': [
            {'value': 'espanol', 'label': 'Español'},
            {'value': 'matematicas', 'label': 'Matemáticas'},
            {'value': 'ciencias', 'label': 'Ciencias'},
            {'value': 'historia', 'label': 'Historia'},
            {'value': 'geografia', 'label': 'Geografía'},
        ],
        'dimensiones': [
            {'value': 'pedagogica', 'label': 'Pedagógica'},
            {'value': 'disciplinar', 'label': 'Disciplinar'},
            {'value': 'didactica', 'label': 'Didáctica'},
        ],
        'tipos_pregunta': [
            {'value': 'opcion_multiple', 'label': 'Opción Múltiple'},
            {'value': 'verdadero_falso', 'label': 'Verdadero/Falso'},
            {'value': 'respuesta_abierta', 'label': 'Respuesta Abierta'},
            {'value': 'relacionar_columnas', 'label': 'Relacionar Columnas'},
        ],
        
        # Preguntas paginadas
        'preguntas': page_obj,
        'pagina_actual': page_obj.number,
        'total_paginas': paginator.num_pages,
        'items_por_pagina': 25,
        'total_registros': 1247
    }
    
    return render(request, 'Evaluador/banco_preguntas.html', context)

def validaciones(request):
    """Revisión de preguntas generadas por IA"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'pendientes_revision': 48,
        'aprobadas_hoy': 15,
        'rechazadas_hoy': 3,
        'total_validadas': 1189,
        
        'pregunta_actual': {
            'id': 'PV-2024-001',
            'origen': 'ia',
            'origen_label': 'Generada por IA',
            'asignatura': 'matematicas',
            'asignatura_label': 'Matemáticas',
            'nivel': 'primaria',
            'dimension': 'pedagogica',
            'nivel_bloom': 'Aplicar',
            'enunciado': 'Un docente observa que varios estudiantes tienen dificultades para entender el concepto de fracciones. ¿Cuál estrategia pedagógica sería más efectiva?',
            'opciones': [
                {
                    'indice': 'A',
                    'texto': 'Diseñar una actividad práctica con material manipulativo donde los estudiantes puedan dividir objetos concretos en partes iguales.',
                    'correcta': True
                },
                {
                    'indice': 'B',
                    'texto': 'Asignar ejercicios matemáticos abstractos con fracciones numéricas complejas.',
                    'correcta': False
                },
                {
                    'indice': 'C',
                    'texto': 'Explicar teóricamente las propiedades matemáticas de las fracciones utilizando fórmulas.',
                    'correcta': False
                },
                {
                    'indice': 'D',
                    'texto': 'Evaluar mediante examen escrito los conocimientos previos sobre números racionales.',
                    'correcta': False
                }
            ],
            'justificacion_ia': 'La opción A es la más alineada con la Nueva Escuela Mexicana porque utiliza el aprendizaje basado en experiencias concretas y materiales manipulativos, lo que facilita la comprensión de conceptos abstractos como las fracciones.',
            'metadata': {
                'id': '#PV-2024-001',
                'origen': 'ia',
                'asignatura': 'Matemáticas',
                'nivel': 'Primaria',
                'dimension': 'Pedagógica',
                'bloom': 'Aplicar'
            }
        },
        
        'preguntas_pendientes': [
            {
                'id': 1,
                'titulo': 'Dificultades con fracciones',
                'origen': 'ia',
                'asignatura': 'matematicas',
                'nivel': 'primaria',
                'activa': True
            },
            {
                'id': 2,
                'titulo': 'Estrategias de lectura',
                'origen': 'ia',
                'asignatura': 'espanol',
                'nivel': 'secundaria',
                'activa': False
            },
            {
                'id': 3,
                'titulo': 'Experimentos científicos',
                'origen': 'ia',
                'asignatura': 'ciencias',
                'nivel': 'primaria',
                'activa': False
            }
        ],
        
        'numero_actual': 1,
        'total_pendientes': 48
    }
    
    return render(request, 'Evaluador/validaciones.html', context)

def chat_ia_evaluador(request):
    """Chat especializado para evaluadores"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'mensajes_iniciales': [
            {
                'tipo': 'bot',
                'contenido': '¡Hola! Soy el Agente Evaluador especializado en procesos USICAMM 2026. ¿En qué puedo ayudarte hoy?',
                'hora': 'Ahora',
                'detalles': [
                    'Procesos de promoción docente',
                    'Normativas y requisitos',
                    'Validaciones de documentos',
                    'Plazos y calendarios'
                ]
            }
        ],
        'preguntas_frecuentes': [
            {
                'id': 1,
                'texto': 'Requisitos de promoción',
                'pregunta_completa': '¿Cuáles son los requisitos para promoción docente?'
            },
            {
                'id': 2,
                'texto': 'Validar documentos',
                'pregunta_completa': '¿Cómo validar documentos en el sistema?'
            },
            {
                'id': 3,
                'texto': 'Normativas aplicables',
                'pregunta_completa': '¿Qué normativas aplican para evaluación 2026?'
            },
            {
                'id': 4,
                'texto': 'Plazos de evaluación',
                'pregunta_completa': '¿Cuáles son los plazos para el proceso 2026?'
            }
        ],
        'usuario_config': {
            'max_caracteres': 100,
            'tiempo_espera': 1000,
            'respuestas_predefinidas': {
                'requisitos': 'Los requisitos para promoción docente incluyen: 1) Antigüedad mínima de 2 años en el nivel actual, 2) Evaluación de competencias con puntaje mínimo de 80 puntos, 3) Portafolio de evidencias validado, 4) Cursos de formación continua actualizados.',
                'validar': 'Para validar documentos en el sistema: 1) Accede a tu portafolio digital, 2) Sube los archivos escaneados en formato PDF, 3) Espera la verificación automática del sistema, 4) Recibirás notificación del estado de validación.',
                'normativas': 'Las normativas aplicables para evaluación 2026: 1) Lineamientos de la Nueva Escuela Mexicana (NEM), 2) Criteria de Evaluación de Carrera Magisterial, 3) Acuerdo Secretarial 09/08/2023, 4) Lineamientos USICAMM 2026.',
                'plazos': 'Los plazos para el proceso 2026: 1) Inicio de registro: Enero 2026, 2) Cierre de inscripciones: Marzo 2026, 3) Período de evaluación: Abril-Junio 2026, 4) Publicación de resultados: Julio 2026.'
            }
        }
    }
    
    return render(request, 'Evaluador/chat_ia.html', context)

def evaluaciones(request):
    """Administración de evaluaciones"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'total_evaluaciones': 12,
        'evaluaciones_borrador': 3,
        'evaluaciones_publicadas': 7,
        'evaluaciones_programadas': 2,
        
        'evaluaciones': [
            {
                'id': 1,
                'titulo': 'Promoción Horizontal 2026 - Matemáticas Primaria',
                'descripcion': 'Evaluación para promoción horizontal de primaria a secundaria con enfoque en competencias matemáticas.',
                'estado': 'publicada',
                'estado_label': 'Publicada',
                'nivel': 'primaria',
                'asignatura': 'matematicas',
                'num_preguntas': 45,
                'fecha_publicacion': '15/06/2024',
                'fecha_vigencia': '30/09/2024',
                'progreso': 65,
                'revisores': [
                    {'iniciales': 'JR', 'aprobado': True},
                    {'iniciales': 'MP', 'aprobado': True},
                    {'iniciales': '?', 'aprobado': False}
                ],
                'acciones_disponibles': {
                    'previsualizar': True,
                    'gestionar': True,
                    'continuar': False,
                    'revisar': False
                }
            },
            {
                'id': 2,
                'titulo': 'Evaluación Diagnóstica NEM - Español Secundaria',
                'descripcion': 'Evaluación inicial para docentes de español sobre lineamientos de la Nueva Escuela Mexicana.',
                'estado': 'borrador',
                'estado_label': 'Borrador',
                'nivel': 'secundaria',
                'asignatura': 'espanol',
                'num_preguntas': 30,
                'fecha_publicacion': '',
                'fecha_vigencia': '',
                'progreso': 35,
                'revisores': [
                    {'iniciales': 'JR', 'aprobado': True},
                    {'iniciales': '?', 'aprobado': False},
                    {'iniciales': '?', 'aprobado': False}
                ],
                'acciones_disponibles': {
                    'previsualizar': True,
                    'gestionar': True,
                    'continuar': True,
                    'revisar': False
                }
            }
        ],
        
        'plantillas': [
            {
                'id': 1,
                'titulo': 'Evaluación Pedagógica Básica',
                'descripcion': 'Plantilla estándar para evaluar competencias pedagógicas según NEM.',
                'num_preguntas': 30,
                'dimension': 'NEM',
                'usos': 15
            },
            {
                'id': 2,
                'titulo': 'Evaluación de Contenidos Disciplinares',
                'descripcion': 'Plantilla especializada para evaluar conocimientos específicos de asignatura.',
                'num_preguntas': 40,
                'dimension': 'Disciplinar',
                'usos': 8
            }
        ]
    }
    
    return render(request, 'Evaluador/evaluaciones.html', context)

def calendario_evaluador(request):
    """Calendario de actividades del evaluador"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'eventos': [
            {
                'id': 1,
                'title': 'Evaluación Promoción Horizontal',
                'start': '2024-06-15T09:00:00',
                'end': '2024-06-15T12:00:00',
                'tipo': 'evaluacion',
                'color': '#e74c3c',
                'descripcion': 'Evaluación para promoción horizontal de primaria a secundaria.',
                'ubicacion': 'En línea',
                'url': '#'
            },
            {
                'id': 2,
                'title': 'Revisión de Banco de Preguntas',
                'start': '2024-06-18T14:00:00',
                'end': '2024-06-18T16:00:00',
                'tipo': 'reunion',
                'color': '#3498db',
                'descripcion': 'Sesión de revisión y validación de preguntas del banco.',
                'ubicacion': 'Sala de Reuniones Virtual',
                'url': '#'
            }
        ],
        
        'proximos_eventos': [
            {
                'id': 1,
                'dia': 15,
                'mes': 'JUN',
                'titulo': 'Evaluación Promoción Horizontal',
                'descripcion': 'Evaluación para promoción horizontal',
                'hora_inicio': '09:00',
                'hora_fin': '12:00',
                'ubicacion': 'En línea',
                'tipo_badge': 'evaluacion',
                'tipo_label': 'Evaluación'
            },
            {
                'id': 2,
                'dia': 18,
                'mes': 'JUN',
                'titulo': 'Revisión de Banco de Preguntas',
                'descripcion': 'Sesión de revisión y validación',
                'hora_inicio': '14:00',
                'hora_fin': '16:00',
                'ubicacion': 'Virtual',
                'tipo_badge': 'reunion',
                'tipo_label': 'Reunión'
            }
        ],
        
        'procesos_usicamm': [
            {
                'nombre': 'Promoción Horizontal 2026',
                'descripcion': 'Evaluación de conocimientos y competencias para cambio de nivel.',
                'tipo': 'evaluacion',
                'fecha_inicio': '04/03/2024',
                'fecha_fin': '30/03/2024',
                'estado': 'en_curso',
                'estado_label': 'En curso',
                'tiempo_restante': '110 días',
                'critico': False
            },
            {
                'nombre': 'Validación de Portafolios',
                'descripcion': 'Revisión y validación de evidencias de desempeño docente.',
                'tipo': 'validacion',
                'fecha_inicio': '01/06/2024',
                'fecha_fin': '30/06/2024',
                'estado': 'en_curso',
                'estado_label': 'En curso',
                'tiempo_restante': '10 días',
                'critico': True
            }
        ]
    }
    
    return render(request, 'Evaluador/calendario.html', context)

def reportes_evaluador(request):
    """Generación de reportes y estadísticas"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'evaluaciones_disponibles': [
            {'value': 'eval-1', 'label': 'Matemáticas Primaria - Nivel 1'},
            {'value': 'eval-2', 'label': 'Español Secundaria - Nivel 2'},
            {'value': 'eval-3', 'label': 'Ciencias Primaria - Nivel 1'},
        ],
        'tipos_reporte': [
            {'value': 'general', 'label': 'Reporte General'},
            {'value': 'preguntas', 'label': 'Análisis por Pregunta'},
            {'value': 'dimensiones', 'label': 'Análisis por Dimensiones'},
            {'value': 'tendencias', 'label': 'Tendencias Temporales'},
        ],
        'niveles_educativos': [
            {'value': 'preescolar', 'label': 'Preescolar'},
            {'value': 'primaria', 'label': 'Primaria'},
            {'value': 'secundaria', 'label': 'Secundaria'},
        ],
        
        'metricas': {
            'confiabilidad_alfa': {
                'valor': 0.87,
                'estado': 'estado-excelente',
                'estado_label': 'Excelente'
            },
            'dificultad_media': {
                'valor': 0.65,
                'estado': 'estado-optimo',
                'estado_label': 'Óptima'
            },
            'tasa_aprobacion': {
                'valor': 82,
                'estado': 'estado-bueno',
                'estado_label': 'Buena'
            }
        },
        
        'distribucion_puntajes': [
            {'rango': '40-50', 'porcentaje': 5, 'valor': 20},
            {'rango': '50-60', 'porcentaje': 12, 'valor': 35},
            {'rango': '60-70', 'porcentaje': 23, 'valor': 68},
            {'rango': '70-80', 'porcentaje': 35, 'valor': 104},
            {'rango': '80-90', 'porcentaje': 20, 'valor': 60},
            {'rango': '90-100', 'porcentaje': 5, 'valor': 15},
        ],
        
        'resultados_dimension': [
            {'dimension': 'Pedagógica', 'porcentaje': 30, 'color': '#3498db'},
            {'dimension': 'Disciplinar', 'porcentaje': 25, 'color': '#2ecc71'},
            {'dimension': 'Didáctica', 'porcentaje': 20, 'color': '#e74c3c'},
            {'dimension': 'Investigación', 'porcentaje': 15, 'color': '#f39c12'},
            {'dimension': 'Gestión', 'porcentaje': 10, 'color': '#9b59b6'},
        ],
        
        'analisis_preguntas': [
            {
                'id': 1,
                'texto_pregunta': '¿Cuál estrategia usarías para enseñar fracciones?',
                'tipo': 'opcion_multiple',
                'tipo_label': 'Opción Múltiple',
                'dificultad': 0.45,
                'dificultad_label': 'Baja',
                'discriminacion': 0.32,
                'porcentaje_aciertos': 68,
                'estado_alerta': False,
                'acciones_disponibles': {
                    'editar': True,
                    'eliminar': True,
                    'analizar': True
                }
            },
            {
                'id': 2,
                'texto_pregunta': 'Explica el principio de equidad educativa',
                'tipo': 'respuesta_abierta',
                'tipo_label': 'Respuesta Abierta',
                'dificultad': 0.78,
                'dificultad_label': 'Alta',
                'discriminacion': 0.45,
                'porcentaje_aciertos': 32,
                'estado_alerta': True,
                'acciones_disponibles': {
                    'editar': True,
                    'eliminar': False,
                    'analizar': True
                }
            }
        ]
    }
    
    return render(request, 'Evaluador/reportes.html', context)

def generador_ia_evaluador(request):
    """Generador de contenido con IA para evaluadores"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'niveles_educativos': [
            {'value': 'preescolar', 'label': 'Preescolar'},
            {'value': 'primaria', 'label': 'Primaria', 'selected': True},
            {'value': 'secundaria', 'label': 'Secundaria'},
        ],
        'asignaturas': [
            {'value': 'matematicas', 'label': 'Matemáticas', 'selected': True},
            {'value': 'espanol', 'label': 'Español'},
            {'value': 'ciencias', 'label': 'Ciencias'},
            {'value': 'historia', 'label': 'Historia'},
            {'value': 'geografia', 'label': 'Geografía'},
        ],
        'dimensiones': [
            {'value': 'pedagogica', 'label': 'Pedagógica', 'selected': True},
            {'value': 'disciplinar', 'label': 'Disciplinar'},
            {'value': 'didactica', 'label': 'Didáctica'},
        ],
        'tipos_pregunta': [
            {'value': 'opcion_multiple', 'label': 'Opción Múltiple', 'selected': True},
            {'value': 'verdadero_falso', 'label': 'Verdadero/Falso'},
            {'value': 'respuesta_abierta', 'label': 'Respuesta Abierta'},
            {'value': 'relacionar_columnas', 'label': 'Relacionar Columnas'},
        ],
        'niveles_bloom': [
            {'value': 'recordar', 'label': 'Recordar'},
            {'value': 'comprender', 'label': 'Comprender', 'selected': True},
            {'value': 'aplicar', 'label': 'Aplicar'},
            {'value': 'analizar', 'label': 'Analizar'},
            {'value': 'evaluar', 'label': 'Evaluar'},
            {'value': 'crear', 'label': 'Crear'},
        ],
        
        'historial_generaciones': [
            {
                'id': 1,
                'fecha': '15/06/2024 14:30',
                'cantidad': 10,
                'asignatura': 'Matemáticas',
                'nivel': 'Primaria',
                'dimension': 'Pedagógica',
                'estado': 'enviado_validacion',
                'estado_label': 'Enviado a validación',
                'acciones_disponibles': {
                    'ver': True,
                    'editar': False,
                    'eliminar': True,
                    'regenerar': True
                }
            },
            {
                'id': 2,
                'fecha': '14/06/2024 10:15',
                'cantidad': 15,
                'asignatura': 'Español',
                'nivel': 'Secundaria',
                'dimension': 'Disciplinar',
                'estado': 'aprobado',
                'estado_label': 'Aprobado',
                'acciones_disponibles': {
                    'ver': True,
                    'editar': False,
                    'eliminar': False,
                    'regenerar': False
                }
            },
            {
                'id': 3,
                'fecha': '13/06/2024 16:45',
                'cantidad': 8,
                'asignatura': 'Ciencias',
                'nivel': 'Primaria',
                'dimension': 'Didáctica',
                'estado': 'observaciones',
                'estado_label': 'Con observaciones',
                'acciones_disponibles': {
                    'ver': True,
                    'editar': True,
                    'eliminar': True,
                    'regenerar': True
                }
            }
        ]
    }
    
    return render(request, 'Evaluador/generador_ia.html', context)