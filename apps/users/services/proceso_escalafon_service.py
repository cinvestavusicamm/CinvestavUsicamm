from apps.users.models import ProcesoEscalafon, Usuario
from django.db.models import Q

class ProcesoEscalafonService:
    
    @staticmethod
    def obtener_procesos_usuario(usuario_id):
        return ProcesoEscalafon.objects.filter(usuario_id=usuario_id).order_by('-fecha_registro')
    
    @staticmethod
    def obtener_proceso_por_folio(folio):
        return ProcesoEscalafon.objects.get(folio=folio)
    
    @staticmethod
    def crear_proceso(usuario_id, folio, tipo_proceso, ciclo_escolar, estado_id, 
                      funcion, tipo_sostenimiento, tipo_valoracion, datos_multifactores, estatus):
        proceso = ProcesoEscalafon(
            usuario_id=usuario_id,
            folio=folio,
            tipo_proceso=tipo_proceso,
            ciclo_escolar=ciclo_escolar,
            estado_id=estado_id,
            funcion=funcion,
            tipo_sostenimiento=tipo_sostenimiento,
            tipo_valoracion=tipo_valoracion,
            datos_multifactores=datos_multifactores,
            estatus=estatus
        )
        proceso.save()
        return proceso
    
    @staticmethod
    def actualizar_estado_proceso(folio, nuevo_estatus):
        proceso = ProcesoEscalafon.objects.get(folio=folio)
        proceso.estatus = nuevo_estatus
        proceso.save()
        return proceso
    
    @staticmethod
    def obtener_procesos_por_estado(estado_id):
        return ProcesoEscalafon.objects.filter(estado_id=estado_id).order_by('-fecha_registro')
    
    @staticmethod
    def obtener_procesos_ciclo_escolar(ciclo_escolar):
        return ProcesoEscalafon.objects.filter(ciclo_escolar=ciclo_escolar).order_by('-fecha_registro')
    