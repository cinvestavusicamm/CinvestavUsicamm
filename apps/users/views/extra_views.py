from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json

@login_required
def prueba(request):
    return render(request, 'prueba.html')

def foros(request):
    """Foros colaborativos de práctica docente"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'categorias_foro': [
            {
                'id': 1,
                'nombre': 'Inclusión Educativa',
                'icono': 'fa-universal-access',
                'posts_count': 156,
                'activa': True
            },
            {
                'id': 2,
                'nombre': 'Saberes Científicos',
                'icono': 'fa-flask',
                'posts_count': 89,
                'activa': False
            },
            {
                'id': 3,
                'nombre': 'Fomento a la Lectura',
                'icono': 'fa-book',
                'posts_count': 234,
                'activa': False
            },
            {
                'id': 4,
                'nombre': 'Proyectos Comunitarios',
                'icono': 'fa-users',
                'posts_count': 67,
                'activa': False
            }
        ],
        'posts_foro': [
            {
                'id': 1,
                'autor': 'Mtro. Ricardo Mendoza',
                'rol': 'SECUNDARIA TÉCNICA 42',
                'titulo': '¿Cómo evaluar campos formativos sin caer en lo cuantitativo?',
                'contenido': 'Compañeros, estoy trabajando el campo de Ética y Naturaleza con mis estudiantes de segundo grado. Me encuentro con el desafío de cómo evaluar realmente el desarrollo de valores y actitudes sin reducir todo a números o escalas. ¿Qué estrategias utilizan para evaluar de manera auténtica estos campos formativos?',
                'fecha': '2024-06-19T08:00:00Z',
                'comentarios': 14,
                'reacciones': 8,
                'resumen_ia_disponible': True,
                'categoria': 'Inclusión Educativa'
            },
            {
                'id': 2,
                'autor': 'Prof. Carmen López',
                'rol': 'PRIMARIA BILINGÜE 15',
                'titulo': 'Experiencias con lectura dialógica en zonas rurales',
                'contenido': 'Quiero compartir mi experiencia implementando lectura dialógica en una comunidad rural. Al principio los padres estaban escépticos, pero ahora los niños están mostrando mejoras significativas en comprensión lectora y expresión oral. Los invito a compartir sus propias estrategias.',
                'fecha': '2024-06-18T16:30:00Z',
                'comentarios': 23,
                'reacciones': 15,
                'resumen_ia_disponible': True,
                'categoria': 'Fomento a la Lectura'
            },
            {
                'id': 3,
                'autor': 'Lic. Jorge Martínez',
                'rol': 'SECUNDARIA GENERAL 08',
                'titulo': 'Proyecto de ciencia comunitaria: purificación de agua',
                'contenido': 'Este ciclo escolar desarrollamos con mis estudiantes un proyecto interdisciplinario para construir sistemas de purificación de agua con materiales reciclados. El proyecto no solo enseñó conceptos científicos sino que generó un impacto real en nuestra comunidad. Comparto los resultados y aprendizajes.',
                'fecha': '2024-06-17T11:45:00Z',
                'comentarios': 31,
                'reacciones': 22,
                'resumen_ia_disponible': False,
                'categoria': 'Proyectos Comunitarios'
            }
        ],
        'asistente_ia': {
            'tema_destacado': 'Inclusión en Zonas Rurales',
            'recurso_sugerido': '[Documento: Orientaciones NEM 2026]',
            'resumen_activo': 'Los posts sobre inclusión en zonas rurales muestran patrones comunes: adaptación curricular, participación comunitaria y uso de recursos locales. Las estrategias más efectivas incluyen el aprendizaje basado en proyectos y la colaboración con familias.'
        }
    }
    
    return render(request, 'Foros.html', context)

def consultar_progreso(request):
    """Portafolio digital del docente"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'portafolio': {
            'evidencias': [
                {
                    'tipo': 'Título Profesional y Cédula',
                    'estado': 'VALIDADO',
                    'descripcion': 'Documento verificado digitalmente vía Cédula Profesional.',
                    'puntos': 15,
                    'icono': 'fa-graduation-cap',
                    'fecha_validacion': '15/01/2024'
                },
                {
                    'tipo': 'Cursos de Formación Continua',
                    'estado': 'PENDIENTE',
                    'progreso': '120 / 200 horas',
                    'puntos': 25,
                    'icono': 'fa-book',
                    'descripcion': 'Se requiere completar 80 horas adicionales'
                },
                {
                    'tipo': 'Experiencia Docente',
                    'estado': 'VALIDADO',
                    'descripcion': 'Antigüedad sistemática verificada: 12 años, 4 meses',
                    'puntos': 20,
                    'icono': 'fa-clock'
                },
                {
                    'tipo': 'Desempeño Profesional',
                    'estado': 'PENDIENTE',
                    'progreso': '65 / 100 puntos',
                    'puntos': 30,
                    'icono': 'fa-chart-line',
                    'descripcion': 'Evaluación de desempeño en proceso'
                },
                {
                    'tipo': 'Investigación y Publicaciones',
                    'estado': 'FALTANTE',
                    'puntos': 10,
                    'icono': 'fa-search',
                    'descripcion': 'No se han registrado publicaciones'
                }
            ],
            'progreso_total': '3/5 COMPLETO',
            'puntaje_actual': 72,
            'puntaje_maximo': 100
        },
        'insights_ia': {
            'riesgo': 'Estás dejando de percibir 15 puntos directos por no completar tu formación continua.',
            'recomendacion': 'Sube tu acta de examen o título de Maestría antes del cierre de la convocatoria para sumar 10 puntos adicionales.',
            'puntaje_actual': '72 / 100',
            'puntaje_posible': '+28 PTS POSIBLES',
            'oportunidades_criticas': [
                'Completa 80 horas de formación continua (+25 pts)',
                'Mejora evaluación de desempeño (+15 pts)',
                'Publica artículo de investigación (+10 pts)'
            ]
        }
    }
    
    return render(request, 'Consultar progreso.html', context)

def cursos_promociones(request):
    """Gestión de cursos y promociones"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'cursos_recomendados': [
            {
                'id': 1,
                'titulo': 'Nueva Escuela Mexicana: Fundamentos',
                'duracion': '40 horas',
                'puntaje': 10,
                'categoria': 'Formación Inicial',
                'disponible': True,
                'descripcion': 'Curso obligatorio sobre principios y lineamientos de la NEM.',
                'modalidad': 'Virtual',
                'inicio': '01/07/2024'
            },
            {
                'id': 2,
                'titulo': 'Competencias Digitales Docentes',
                'duracion': '60 horas',
                'puntaje': 15,
                'categoria': 'Formación Continua',
                'disponible': True,
                'descripcion': 'Desarrollo de habilidades tecnológicas para el aula digital.',
                'modalidad': 'Híbrida',
                'inicio': '15/07/2024'
            },
            {
                'id': 3,
                'titulo': 'Neurodidáctica y Aprendizaje',
                'duracion': '50 horas',
                'puntaje': 12,
                'categoria': 'Especialización',
                'disponible': False,
                'descripcion': 'Aplicación de principios neurocientíficos a la enseñanza.',
                'modalidad': 'Virtual',
                'inicio': '01/08/2024'
            }
        ],
        'promociones_disponibles': [
            {
                'id': 1,
                'titulo': 'Promoción Horizontal 2026',
                'descripcion': 'Oportunidad para cambio de nivel sin cambio de plaza',
                'tipo': 'horizontal',
                'fecha_limite': '2026-03-31',
                'requisitos': [
                    '3 años antigüedad en el nivel actual',
                    '80 puntos evaluación',
                    'Portafolio completo',
                    '200 horas formación continua'
                ],
                'plazas_disponibles': 150,
                'estado': 'disponible'
            },
            {
                'id': 2,
                'titulo': 'Promoción Vertical Primaria-Secundaria',
                'descripcion': 'Ascenso a nivel educativo superior con cambio de plaza',
                'tipo': 'vertical',
                'fecha_limite': '2026-02-28',
                'requisitos': [
                    '5 años antigüedad mínima',
                    '85 puntos evaluación',
                    'Examen de competencia',
                    '250 horas formación específica'
                ],
                'plazas_disponibles': 75,
                'estado': 'disponible'
            }
        ],
        'puntajes_acumulados': {
            'formacion_inicial': 30,
            'formacion_continua': 15,
            'desempeno': 25,
            'antiguedad': 20,
            'total': 90
        },
        'recomendacion_ia': {
            'titulo': 'Ruta Óptima de Promoción',
            'descripcion': 'Basado en tu perfil actual, te recomendamos enfocarte en la Promoción Horizontal 2026. Cumples con el 75% de los requisitos y solo necesitas completar 80 horas más de formación continua.',
            'probabilidad_exito': 85,
            'tiempo_preparacion': '6 meses'
        }
    }
    
    return render(request, 'cursos y promociones.html', context)

def rutas_promocion(request):
    """Rutas de promoción"""
    if not request.session.get('usuario_id'):
        return redirect('sesion')
    
    context = {
        'convocatorias_activas': [
            {
                'id': 1,
                'titulo': 'Promoción Horizontal Primaria-Secundaria 2026',
                'tipo': 'horizontal',
                'estado': 'disponible',
                'fecha_inicio': '2024-12-01',
                'fecha_fin': '2026-03-31',
                'plazas_disponibles': 150,
                'plazas_cubiertas': 87,
                'descripcion': 'Oportunidad para docentes de primaria que desean cambiar a secundaria manteniendo su plaza actual.'
            },
            {
                'id': 2,
                'titulo': 'Promoción Vertical Educación Básica 2026',
                'tipo': 'vertical',
                'estado': 'disponible',
                'fecha_inicio': '2025-01-15',
                'fecha_fin': '2026-02-28',
                'plazas_disponibles': 200,
                'plazas_cubiertas': 134,
                'descripcion': 'Ascenso en la carrera magisterial con cambio de nivel y mejora salarial.'
            },
            {
                'id': 3,
                'titulo': 'Incorporación a Carrera Magisterial',
                'tipo': 'incorporacion',
                'estado': 'proxima',
                'fecha_inicio': '2025-03-01',
                'fecha_fin': '2026-04-30',
                'plazas_disponibles': 300,
                'plazas_cubiertas': 0,
                'descripcion': 'Proceso de incorporación para docentes sin plaza definitiva.'
            }
        ],
        'requisitos_promocion': [
            {
                'categoria': 'Antigüedad',
                'descripcion': 'Mínimo 3 años en el nivel actual',
                'cumplido': True,
                'puntaje_asignado': 20
            },
            {
                'categoria': 'Evaluación',
                'descripcion': 'Puntaje mínimo de 80 puntos',
                'cumplido': False,
                'puntaje_actual': 72,
                'puntaje_requerido': 80,
                'puntaje_asignado': 30
            },
            {
                'categoria': 'Formación',
                'descripcion': '200 horas de formación continua',
                'cumplido': False,
                'horas_actuales': 120,
                'horas_requeridas': 200,
                'puntaje_asignado': 25
            },
            {
                'categoria': 'Portafolio',
                'descripcion': 'Evidencias de desempeño completas',
                'cumplido': True,
                'puntaje_asignado': 25
            }
        ],
        'timeline_proceso': [
            {
                'etapa': 'Registro',
                'fecha_inicio': '2024-12-01',
                'fecha_fin': '2024-12-31',
                'estado': 'completado',
                'descripcion': 'Período de inscripción y documentación inicial.'
            },
            {
                'etapa': 'Evaluación',
                'fecha_inicio': '2025-01-15',
                'fecha_fin': '2025-02-28',
                'estado': 'en_progreso',
                'descripcion': 'Aplicación de exámenes y evaluación de competencias.'
            },
            {
                'etapa': 'Validación',
                'fecha_inicio': '2025-03-01',
                'fecha_fin': '2025-03-31',
                'estado': 'pendiente',
                'descripcion': 'Revisión y validación de documentos y evidencias.'
            },
            {
                'etapa': 'Resultados',
                'fecha_inicio': '2026-04-01',
                'fecha_fin': '2026-04-15',
                'estado': 'pendiente',
                'descripcion': 'Publicación de resultados y asignación de plazas.'
            }
        ],
        'analisis_ia': {
            'idoneidad_perfil': 78,
            'recomendacion_principal': 'Enfocarse en completar horas de formación continua',
            'fortalezas': [
                'Sólida antigüedad en el nivel actual',
                'Portafolio de evidencias completo',
                'Buen desempeño evaluación anterior'
            ],
            'areas_mejora': [
                'Completar 80 horas de formación continua',
                'Mejorar puntaje de evaluación en 8 puntos',
                'Actualizar documentación de especialización'
            ]
        }
    }
    
    return render(request, 'Rutas y promociones.html', context)
