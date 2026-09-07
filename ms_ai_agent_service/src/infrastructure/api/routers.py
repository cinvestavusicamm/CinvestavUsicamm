from fastapi import APIRouter
import re

from src.domain.schemas import ChatRequest, ChatResponse, EvaluateRequest, EvaluateResponse, QuestionRequest, QuestionResponse

router = APIRouter(tags=["IA"])

@router.post("/ai/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    prompt = payload.prompt.lower()
    prompt_original = payload.prompt
    
    # Detectar solicitud de generación de curso completo
    if any(word in prompt for word in ["hazme un curso", "crea un curso", "genera un curso", "curso sobre", "curso de"]):
        # Extraer el tema del curso
        import re
        tema_match = re.search(r'(?:curso|sobre|de)\s+(.+?)(?:\s|$)', prompt_original)
        tema = tema_match.group(1).strip() if tema_match else "General"
        
        respuesta_json = {
            "mensaje_chat": f"Voy a generar un curso completo sobre '{tema}'. Estructurando los módulos y contenido...",
            "tipo_accion": "generar_curso_completo",
            "datos": {
                "titulo": f"Curso de {tema}",
                "descripcion": f"Curso completo sobre {tema} diseñado para desarrollar competencias profesionales.",
                "duracion": "40 horas",
                "modulos": [
                    {
                        "numero": 1,
                        "titulo": f"Introducción a {tema}",
                        "contenido": f"En este módulo exploraremos los fundamentos básicos de {tema} y su importancia en el contexto actual."
                    },
                    {
                        "numero": 2,
                        "titulo": f"Desarrollo de {tema}",
                        "contenido": f"Profundizaremos en los conceptos avanzados de {tema} y su aplicación práctica."
                    },
                    {
                        "numero": 3,
                        "titulo": f"Aplicación de {tema}",
                        "contenido": f"Analizaremos casos de estudio y aplicaremos los conocimientos de {tema} en situaciones reales."
                    }
                ],
                "examen": {
                    "preguntas": [
                        {
                            "pregunta": f"¿Cuál es la importancia de {tema} en el contexto actual?",
                            "opciones": ["A) Muy limitada", "B) Moderada", "C) Fundamental", "D) Nula"],
                            "correcta": "C"
                        },
                        {
                            "pregunta": f"¿Qué competencias se desarrollan al estudiar {tema}?",
                            "opciones": ["A) Solo teóricas", "B) Solo prácticas", "C) Teóricas y prácticas", "D) Ninguna"],
                            "correcta": "C"
                        }
                    ]
                }
            }
        }
        return ChatResponse(reply=str(respuesta_json))
    
    # Detectar cuando el usuario da preguntas específicas para integrar
    if any(word in prompt for word in ["integra", "integre", "integres", "integren", "pon", "ponga", "coloca", "coloca"]):
        if "pregunta" in prompt:
            # Extraer las preguntas específicas del usuario
            if "¿" in prompt_original or "?" in prompt_original:
                # Extraer solo las preguntas específicas (todo después de "¿" o "?")
                import re
                preguntas_extraidas = re.findall(r'[¿?][^¿?]*[¿?]', prompt_original)
                if preguntas_extraidas:
                    preguntas_texto = '\n'.join(preguntas_extraidas)
                    # Devolver JSON estructurado
                    respuesta_json = {
                        "mensaje_chat": "He integrado las preguntas solicitadas en el módulo.",
                        "tipo_accion": "insertar_preguntas",
                        "datos": [
                            {
                                "pregunta": preg.strip("¿?"),
                                "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                                "correcta": "A"
                            } for preg in preguntas_extraidas
                        ]
                    }
                    return ChatResponse(reply=str(respuesta_json))
                else:
                    # Si no se encuentran con signos, extraer el contenido después de "preguntas"
                    if "preguntas" in prompt:
                        inicio = prompt.find("preguntas") + len("preguntas")
                        preguntas_texto = prompt_original[inicio:].strip()
                        respuesta_json = {
                            "mensaje_chat": "He integrado las preguntas solicitadas en el módulo.",
                            "tipo_accion": "insertar_preguntas",
                            "datos": [
                                {
                                    "pregunta": preguntas_texto.strip("¿?"),
                                    "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                                    "correcta": "A"
                                }
                            ]
                        }
                        return ChatResponse(reply=str(respuesta_json))
                    else:
                        respuesta_json = {
                            "mensaje_chat": "He procesado tu solicitud.",
                            "tipo_accion": "texto_plano",
                            "datos": [{"texto": prompt_original}]
                        }
                        return ChatResponse(reply=str(respuesta_json))
            else:
                respuesta_json = {
                    "mensaje_chat": "He procesado tu solicitud.",
                    "tipo_accion": "texto_plano",
                    "datos": [{"texto": prompt_original}]
                }
                return ChatResponse(reply=str(respuesta_json))
        else:
            respuesta_json = {
                "mensaje_chat": "He procesado tu solicitud.",
                "tipo_accion": "texto_plano",
                "datos": [{"texto": prompt_original}]
            }
            return ChatResponse(reply=str(respuesta_json))
    
    # Detectar solicitudes de contenido educativo general
    elif any(word in prompt for word in ["módulo", "modulo", "pregunta", "preguntas", "examen", "redacta", "redactar", "texto", "contenido"]):
        # Detectar si el usuario especifica tipo de preguntas
        es_opcion_multiple = any(word in prompt for word in ["opción múltiple", "opcion multiple", "multiple choice", "opciones", "a) b) c) d)"])
        es_abierta = any(word in prompt for word in ["abierta", "abiertas", "respuesta corta", "ensayo"])
        
        # Detectar cantidad de preguntas solicitada
        import re
        cantidad_match = re.search(r'(\d+)\s*(?:pregunta|question|p)', prompt)
        cantidad = int(cantidad_match.group(1)) if cantidad_match else 5
        
        # Detectar tema principal
        temas_conocidos = {
            "barcelona": {
                "nombre": "FC Barcelona",
                "preguntas_opcion_multiple": [
                    {
                        "pregunta": "¿Cuándo fue fundado el FC Barcelona?",
                        "opciones": ["A) 1899", "B) 1902", "C) 1910", "D) 1920"],
                        "correcta": "A"
                    },
                    {
                        "pregunta": "¿Quién es el máximo goleador histórico del club?",
                        "opciones": ["A) Lionel Messi", "B) Cristiano Ronaldo", "C) Xavi Hernández", "D) Andrés Iniesta"],
                        "correcta": "A"
                    },
                    {
                        "pregunta": "¿Cuántas Champions League ha ganado el Barcelona?",
                        "opciones": ["A) 3", "B) 5", "C) 7", "D) 10"],
                        "correcta": "B"
                    },
                    {
                        "pregunta": "¿Cuál es el estadio oficial del FC Barcelona?",
                        "opciones": ["A) Santiago Bernabéu", "B) Camp Nou", "C) Wembley", "D) San Siro"],
                        "correcta": "B"
                    },
                    {
                        "pregunta": "¿Quién es el entrenador actual del Barcelona?",
                        "opciones": ["A) Carlo Ancelotti", "B) Jürgen Klopp", "C) Hansi Flick", "D) Pep Guardiola"],
                        "correcta": "C"
                    }
                ],
                "preguntas_abiertas": [
                    "Describe la importancia del FC Barcelona en la historia del fútbol mundial.",
                    "Explica el estilo de juego característico del Barcelona y su influencia en el fútbol moderno.",
                    "Analiza el impacto de La Masía en el desarrollo de talentos del club.",
                    "¿Cuáles han sido los momentos más importantes en la historia del Barcelona?",
                    "Compara el Barcelona con otros grandes clubes europeos en términos de logros."
                ]
            },
            "real madrid": {
                "nombre": "Real Madrid",
                "preguntas_opcion_multiple": [
                    {
                        "pregunta": "¿Cuántas Champions League ha ganado el Real Madrid?",
                        "opciones": ["A) 10", "B) 12", "C) 14", "D) 15"],
                        "correcta": "D"
                    },
                    {
                        "pregunta": "¿Quién es el máximo goleador histórico del Real Madrid?",
                        "opciones": ["A) Cristiano Ronaldo", "B) Raúl González", "C) Alfredo Di Stéfano", "D) Karim Benzema"],
                        "correcta": "A"
                    },
                    {
                        "pregunta": "¿Cuál es el estadio oficial del Real Madrid?",
                        "opciones": ["A) Camp Nou", "B) Santiago Bernabéu", "C) Old Trafford", "D) San Siro"],
                        "correcta": "B"
                    },
                    {
                        "pregunta": "¿En qué año fue fundado el Real Madrid?",
                        "opciones": ["A) 1899", "B) 1902", "C) 1905", "D) 1910"],
                        "correcta": "B"
                    },
                    {
                        "pregunta": "¿Quién es el entrenador actual del Real Madrid?",
                        "opciones": ["A) Carlo Ancelotti", "B) Zinedine Zidane", "C) José Mourinho", "D) Jürgen Klopp"],
                        "correcta": "A"
                    }
                ],
                "preguntas_abiertas": [
                    "Analiza la importancia del Real Madrid en la historia del fútbol europeo.",
                    "Describe la filosofía del Real Madrid y su impacto en el fútbol mundial.",
                    "¿Cuáles son los logros más significativos del Real Madrid en competiciones europeas?",
                    "Explica la influencia del Real Madrid en el desarrollo del fútbol moderno.",
                    "Compara el estilo de juego del Real Madrid con otros grandes clubes europeos."
                ]
            }
        }
        
        # Detectar el tema en el prompt
        tema_detectado = None
        for tema_key, tema_data in temas_conocidos.items():
            if tema_key in prompt:
                tema_detectado = tema_data
                break
        
        if tema_detectado:
            # Generar preguntas según el tema detectado
            if es_opcion_multiple or (not es_abierta and not es_opcion_multiple):
                # Por defecto opción múltiple si no se especifica
                preguntas_disponibles = tema_detectado["preguntas_opcion_multiple"]
                preguntas_seleccionadas = preguntas_disponibles[:cantidad]
                
                respuesta_json = {
                    "mensaje_chat": f"Aquí tienes {len(preguntas_seleccionadas)} preguntas de opción múltiple sobre {tema_detectado['nombre']}.",
                    "tipo_accion": "insertar_preguntas",
                    "datos": preguntas_seleccionadas
                }
                return ChatResponse(reply=str(respuesta_json))
                    
            elif es_abierta:
                preguntas_disponibles = tema_detectado["preguntas_abiertas"]
                preguntas_seleccionadas = preguntas_disponibles[:cantidad]
                
                datos_abiertas = [
                    {
                        "pregunta": preg,
                        "opciones": [],
                        "correcta": "",
                        "tipo": "abierta"
                    } for preg in preguntas_seleccionadas
                ]
                
                respuesta_json = {
                    "mensaje_chat": f"Aquí tienes {len(preguntas_seleccionadas)} preguntas abiertas sobre {tema_detectado['nombre']}.",
                    "tipo_accion": "insertar_preguntas",
                    "datos": datos_abiertas
                }
                return ChatResponse(reply=str(respuesta_json))
            else:
                # Si no se especifica tipo, preguntar
                respuesta_json = {
                    "mensaje_chat": f"He detectado que quieres {cantidad} preguntas sobre {tema_detectado['nombre']}. ¿Prefieres que sean de opción múltiple o preguntas abiertas?",
                    "tipo_accion": "seleccionar_tipo_preguntas",
                    "datos": {
                        "cantidad": cantidad,
                        "tema": tema_detectado['nombre']
                    }
                }
                return ChatResponse(reply=str(respuesta_json))
        else:
            # Tema no reconocido - generar preguntas genéricas
            if es_opcion_multiple or (not es_abierta and not es_opcion_multiple):
                preguntas_genericas = [
                    {
                        "pregunta": "¿Cuál es el objetivo principal de este tema?",
                        "opciones": ["A) Aprender conceptos básicos", "B) Desarrollar habilidades prácticas", "C) Analizar casos de estudio", "D) Todos los anteriores"],
                        "correcta": "D"
                    },
                    {
                        "pregunta": "¿Qué competencias se desarrollarán?",
                        "opciones": ["A) Análisis crítico", "B) Resolución de problemas", "C) Comunicación efectiva", "D) Todas las anteriores"],
                        "correcta": "D"
                    },
                    {
                        "pregunta": "¿Cómo se evaluará el aprendizaje?",
                        "opciones": ["A) Examen teórico", "B) Proyecto práctico", "C) Participación en clase", "D) Combinación de métodos"],
                        "correcta": "D"
                    },
                    {
                        "pregunta": "¿Cuál es la duración recomendada?",
                        "opciones": ["A) 10 horas", "B) 20 horas", "C) 30 horas", "D) 40 horas"],
                        "correcta": "B"
                    },
                    {
                        "pregunta": "¿Qué recursos se necesitan?",
                        "opciones": ["A) Material de lectura", "B) Software especializado", "C) Acceso a internet", "D) Todos los anteriores"],
                        "correcta": "D"
                    }
                ]
                
                respuesta_json = {
                    "mensaje_chat": f"Aquí tienes {cantidad} preguntas de opción múltiple generadas.",
                    "tipo_accion": "insertar_preguntas",
                    "datos": preguntas_genericas[:cantidad]
                }
                return ChatResponse(reply=str(respuesta_json))
            elif es_abierta:
                preguntas_abiertas_genericas = [
                    "Explica la importancia del tema en el contexto actual.",
                    "Describe los conceptos fundamentales y su aplicación práctica.",
                    "Analiza los desafíos principales relacionados con este tema.",
                    "¿Cómo se relaciona este tema con otras áreas de conocimiento?",
                    "Propone soluciones para mejorar la comprensión del tema."
                ]
                
                datos_abiertas = [
                    {
                        "pregunta": preg,
                        "opciones": [],
                        "correcta": "",
                        "tipo": "abierta"
                    } for preg in preguntas_abiertas_genericas[:cantidad]
                ]
                
                respuesta_json = {
                    "mensaje_chat": f"Aquí tienes {cantidad} preguntas abiertas generadas.",
                    "tipo_accion": "insertar_preguntas",
                    "datos": datos_abiertas
                }
                return ChatResponse(reply=str(respuesta_json))
            else:
                respuesta_json = {
                    "mensaje_chat": f"Quiero generar {cantidad} preguntas, pero necesito que me especifiques si prefieres opción múltiple o preguntas abiertas.",
                    "tipo_accion": "seleccionar_tipo_preguntas",
                    "datos": {"cantidad": cantidad}
                }
                return ChatResponse(reply=str(respuesta_json))
    
    # Detectar solicitudes de preguntas mixtas
    elif "mixta" in prompt or "mixtas" in prompt:
        cantidad_match = re.search(r'(\d+)\s*(?:pregunta|question|p)', prompt)
        cantidad = int(cantidad_match.group(1)) if cantidad_match else 5
        
        # Generar mixta: mitad opción múltiple, mitad abiertas
        preguntas_mixtas = []
        
        # Preguntas de opción múltiple
        preguntas_opcion_multiple = [
            {
                "pregunta": "¿Cuál es el objetivo principal de este tema?",
                "opciones": ["A) Aprender conceptos básicos", "B) Desarrollar habilidades prácticas", "C) Analizar casos de estudio", "D) Todos los anteriores"],
                "correcta": "D"
            },
            {
                "pregunta": "¿Qué competencias se desarrollarán?",
                "opciones": ["A) Análisis crítico", "B) Resolución de problemas", "C) Comunicación efectiva", "D) Todas las anteriores"],
                "correcta": "D"
            },
            {
                "pregunta": "¿Cómo se evaluará el aprendizaje?",
                "opciones": ["A) Examen teórico", "B) Proyecto práctico", "C) Participación en clase", "D) Combinación de métodos"],
                "correcta": "D"
            }
        ]
        
        # Preguntas abiertas
        preguntas_abiertas = [
            "Explica la importancia del tema en el contexto actual.",
            "Describe los conceptos fundamentales y su aplicación práctica."
        ]
        
        # Combinar preguntas
        mitad = cantidad // 2
        for i in range(min(mitad, len(preguntas_opcion_multiple))):
            preguntas_mixtas.append(preguntas_opcion_multiple[i])
        
        for i in range(min(cantidad - mitad, len(preguntas_abiertas))):
            preguntas_mixtas.append({
                "pregunta": preguntas_abiertas[i],
                "opciones": [],
                "correcta": "",
                "tipo": "abierta"
            })
        
        respuesta_json = {
            "mensaje_chat": f"Aquí tienes {len(preguntas_mixtas)} preguntas mixtas (opción múltiple y abiertas).",
            "tipo_accion": "insertar_preguntas",
            "datos": preguntas_mixtas
        }
        return ChatResponse(reply=str(respuesta_json))
        
        return ChatResponse(reply=str(respuesta_json))
    else:
        respuesta_json = {
            "mensaje_chat": f"Tutor virtual: he recibido tu mensaje '{payload.prompt}' y estoy trabajando en una respuesta. Para generaciones de contenido educativo, por favor especifica claramente el tema y el tipo de contenido que necesitas (preguntas, texto explicativo, etc.).",
            "tipo_accion": "texto_plano",
            "datos": [{"texto": payload.prompt}]
        }
        return ChatResponse(reply=str(respuesta_json))

@router.post("/ai/evaluar", response_model=EvaluateResponse)
async def evaluar(payload: EvaluateRequest):
    return EvaluateResponse(score=85.0, summary="EvaluaciÃ³n automÃ¡tica generada para el texto proporcionado.")

@router.post("/ai/generar-preguntas", response_model=QuestionResponse)
async def generar_preguntas(payload: QuestionRequest):
    return QuestionResponse(
        questions=[
            "Â¿CuÃ¡l es el objetivo principal de este tema?",
            "Enumera 3 conceptos clave relacionados con la materia.",
        ]
    )
