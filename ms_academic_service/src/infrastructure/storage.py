from src.domain.schemas import Student, Teacher, Group

alumnos = [
    Student(id=1, nombre="Ana PÃ©rez", grado="3Â°", grupo="A"),
    Student(id=2, nombre="Luis MartÃ­nez", grado="4Â°", grupo="B"),
]

profesores = [
    Teacher(id=1, nombre="Mtra. GarcÃ­a", materia="MatemÃ¡ticas", turno="Matutino"),
    Teacher(id=2, nombre="Mtro. LÃ³pez", materia="Historia", turno="Vespertino"),
]

grupos = [
    Group(id=1, nombre="A", grado="3Â°", salon="101"),
    Group(id=2, nombre="B", grado="4Â°", salon="102"),
]
