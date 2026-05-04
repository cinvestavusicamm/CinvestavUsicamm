from django.contrib.auth.hashers import make_password
from apps.users.models import Usuario, Rol, Institucion

class UserService:

    @staticmethod
    def obtener_usuario(usuario_id):
        return Usuario.objects.select_related('rol', 'institucion').get(id_usuario=usuario_id)
    
    @staticmethod
    def crear_usuario(data):
        usuario_data = data.copy()

        if usuario_data.get("contrasena"):
            usuario_data["contrasena"] = make_password(usuario_data["contrasena"])

        usuario_data["activo"] = usuario_data.get("activo", True)

        return Usuario.objects.create(**usuario_data)
    
    @staticmethod
    def editar_usuario(usuario_id, data):
        usuario = UserService.obtener_usuario(usuario_id)

        for campo in (
            "nombre",
            "apellido_paterno",
            "apellido_materno",
            "correo",
            "curp",
        ):
            if data.get(campo) is not None:
                setattr(usuario, campo, data.get(campo))

        if data.get("rol"):
            usuario.rol = UserService.obtener_rol(data["rol"])

        if data.get("institucion"):
            usuario.institucion = Institucion.objects.get(id_institucion=data["institucion"])

        if data.get("contrasena"):
            usuario.contrasena = make_password(data["contrasena"])

        usuario.save()
        return usuario
    
    @staticmethod
    def alternar_activo(usuario_id):
        usuario = UserService.obtener_usuario(usuario_id)
        usuario.activo = not usuario.activo
        usuario.save(update_fields=["activo"])
        return usuario

    @staticmethod
    def obtener_rol(valor):
        if str(valor).isdigit():
            return Rol.objects.get(id_rol=valor)

        return Rol.objects.get(nombre_rol=valor)

    @staticmethod
    def obtener_contadores():
        total = Usuario.objects.count()
        activos = Usuario.objects.filter(activo=True).count()

        return {
            "total": total,
            "activos": activos,
            "en_revision": total - activos,
        }
    
