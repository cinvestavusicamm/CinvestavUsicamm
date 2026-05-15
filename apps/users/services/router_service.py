class RouterService:

    @staticmethod
    def decidir(pregunta: str):
        pregunta = pregunta.lower()

        keywords_bd = [
            "plaza",
            "plazas",
            "docente",
            "docentes",
            "maestro",
            "maestros",
            "usuario",
            "usuarios",
            "registro",
            "datos"
        ]

        for palabra in keywords_bd:
            if palabra in pregunta:
                return "bd"

        return "agente"