from django.contrib.auth.hashers import make_password
from django.db import transaction

from apps.users.config.constants import ROLE_ADMIN
from apps.users.models import Usuario, Rol, Institucion


class OperacionRechazada(Exception):
    """Regla de negocio que impide la operacion.

    La traduce la vista a HTTP. Vive en el servicio, no en la vista, para
    que ningun llamante pueda saltarsela: hoy el auto-bloqueo de
    desactivacion estaba en la vista y un llamante nuevo no lo tendria.
    """

    status = 400

    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class AutoDesactivacionRechazada(OperacionRechazada):
    """El ADMIN intenta desactivarse a si mismo. 400: la peticion es invalida."""


class AutoCambioRolRechazado(OperacionRechazada):
    """El ADMIN intenta cambiarse su propio rol. 400: la peticion es invalida."""


class SinAdminActivo(OperacionRechazada):
    """La operacion dejaria el sistema sin ningun ADMIN activo.

    409 y no 400: la peticion es valida en forma, pero choca con el estado
    actual del sistema. 400 induciria a retry sin cambios.
    """

    status = 409


class UserService:

    @staticmethod
    def obtener_usuario(usuario_id):
        return Usuario.objects.select_related('rol', 'institucion').get(id_usuario=usuario_id)

    @staticmethod
    def _admins_activos_bloqueados():
        """IDs de los ADMIN activos, con la fila bloqueada.

        select_for_update no hace nada en SQLite: Django lo ignora en
        silencio porque el backend no declara la característica. Ahi el
        codigo corre y el test pasa, pero no hay garantia de nada. En
        PostgreSQL serializa a los ADMIN concurrentes.

        order_by fija el orden en que se toman los bloqueos. Sin el, dos
        transacciones que bloqueen el mismo conjunto en orden distinto se
        quedan esperando la una a la otra y PostgreSQL aborta una con error
        de serializacion.
        """
        return list(
            Usuario.objects
            .select_for_update()
            .filter(activo=True, rol__nombre_rol=ROLE_ADMIN)
            .order_by('id_usuario')
            .values_list('id_usuario', flat=True)
        )

    @staticmethod
    def _verificar_que_sobrevive_un_admin(objetivo, admins_activos, mensaje):
        """Impide quedarse sin ningun ADMIN activo.

        Solo bloquea cuando el objetivo es un ADMIN activo y la operacion
        lo va a dejar fuera: si sigue como ADMIN, o si nunca fue ADMIN,
        quitar a otro no importa.
        """
        if not objetivo.activo or objetivo.rol.nombre_rol != ROLE_ADMIN:
            return

        if admins_activos != [objetivo.id_usuario]:
            return

        raise SinAdminActivo(mensaje, codigo='sin_admin_activo')

    @staticmethod
    def crear_usuario(data):
        usuario_data = data.copy()

        if usuario_data.get("contrasena"):
            usuario_data["contrasena"] = make_password(usuario_data["contrasena"])

        usuario_data["activo"] = usuario_data.get("activo", True)

        return Usuario.objects.create(**usuario_data)

    @staticmethod
    def editar_usuario(usuario_id, data, actor_id=None):
        """Edita un usuario aplicando las reglas de proteccion del ADMIN.

        actor_id es quien pide el cambio, no a quien se edita. Es lo que
        permite distinguir "te estas editando a ti mismo" de "estas
        editando a otro".
        """
        with transaction.atomic():
            usuario = (
                Usuario.objects
                .select_for_update()
                .select_related('rol')
                .get(id_usuario=usuario_id)
            )

            nuevo_rol = UserService.obtener_rol(data["rol"]) if data.get("rol") else None

            es_el_actor = actor_id is not None and int(actor_id) == usuario.id_usuario

            if nuevo_rol is not None and es_el_actor and nuevo_rol.id_rol != usuario.rol_id:
                raise AutoCambioRolRechazado(
                    'No puedes cambiar tu propio rol',
                    codigo='auto_cambio_rol',
                )

            degradado = (
                nuevo_rol is not None
                and usuario.rol.nombre_rol == ROLE_ADMIN
                and nuevo_rol.nombre_rol != ROLE_ADMIN
            )
            if degradado:
                UserService._verificar_que_sobrevive_un_admin(
                    usuario,
                    UserService._admins_activos_bloqueados(),
                    'No puedes quitarle el rol de administrador al unico '
                    'administrador activo del sistema',
                )

            for campo in (
                "nombre",
                "apellido_paterno",
                "apellido_materno",
                "correo",
                "curp",
            ):
                if data.get(campo) is not None:
                    setattr(usuario, campo, data.get(campo))

            if nuevo_rol is not None:
                usuario.rol = nuevo_rol

            if data.get("institucion"):
                usuario.institucion = Institucion.objects.get(id_institucion=data["institucion"])

            if data.get("contrasena"):
                usuario.contrasena = make_password(data["contrasena"])

            usuario.save()
            return usuario

    @staticmethod
    def alternar_activo(usuario_id, actor_id=None):
        with transaction.atomic():
            usuario = (
                Usuario.objects
                .select_for_update()
                .select_related('rol')
                .get(id_usuario=usuario_id)
            )

            # Alternar un usuario que esta activo lo apaga, y ese es el
            # sentido que vigilar. futuro_activo es lo que quedara guardado.
            va_a_desactivar = usuario.activo
            futuro_activo = not va_a_desactivar

            if va_a_desactivar and actor_id is not None and int(actor_id) == usuario.id_usuario:
                raise AutoDesactivacionRechazada(
                    'No puedes desactivar tu propia cuenta',
                    codigo='auto_desactivacion',
                )

            if va_a_desactivar:
                UserService._verificar_que_sobrevive_un_admin(
                    usuario,
                    UserService._admins_activos_bloqueados(),
                    'No puedes desactivar al unico administrador activo del sistema',
                )

            usuario.activo = futuro_activo
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