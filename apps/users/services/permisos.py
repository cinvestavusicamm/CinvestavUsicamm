def es_evaluador(user):
    return getattr(user, 'rol', None) == 'EVALUADOR'

def es_admin(user):
    return getattr(user, 'rol', None) == 'ADMIN'

def es_generador(user):
    return getattr(user, 'rol', None) == 'GENERADOR'
