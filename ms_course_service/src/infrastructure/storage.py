from src.domain.schemas import Course, Module, Resource

cursos = [
    Course(
        id=1,
        nombre="IntroducciÃ³n a ProgramaciÃ³n",
        descripcion="Curso base de lÃ³gica y sintaxis.",
        modulos=[
            Module(
                id=1,
                titulo="Variables y Tipos",
                descripcion="Fundamentos bÃ¡sicos de programaciÃ³n.",
                recursos=[
                    Resource(id=1, tipo="video", titulo="Variables", enlace="https://example.com/variables"),
                ],
            )
        ],
    )
]
