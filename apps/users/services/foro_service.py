from apps.users.models import Foro, PostForo


class ForoService:

    @staticmethod
    def obtener_foros_curso(curso_id):
        return Foro.objects.filter(
            curso_id=curso_id,
            activo=True
        ).order_by("-fecha_creacion")

    @staticmethod
    def obtener_foro_por_id(foro_id):
        return Foro.objects.get(id_foro=foro_id)

    @staticmethod
    def crear_foro(curso_id, titulo, descripcion):
        return Foro.objects.create(
            curso_id=curso_id,
            titulo=titulo,
            descripcion=descripcion,
        )

    @staticmethod
    def actualizar_foro(foro_id, titulo=None, descripcion=None):
        foro = ForoService.obtener_foro_por_id(foro_id)

        if titulo is not None:
            foro.titulo = titulo
        if descripcion is not None:
            foro.descripcion = descripcion

        foro.save()
        return foro

    @staticmethod
    def desactivar_foro(foro_id):
        foro = ForoService.obtener_foro_por_id(foro_id)
        foro.activo = False
        foro.save(update_fields=["activo"])
        return foro

    @staticmethod
    def obtener_posts_foro(foro_id):
        return PostForo.objects.filter(foro_id=foro_id).order_by("-fecha_creacion")

    @staticmethod
    def crear_post(foro_id, autor_id, contenido):
        return PostForo.objects.create(
            foro_id=foro_id,
            autor_id=autor_id,
            contenido=contenido,
        )

    @staticmethod
    def actualizar_post(post_id, contenido):
        post = PostForo.objects.get(id_post=post_id)
        post.contenido = contenido
        post.save(update_fields=["contenido", "fecha_edicion"])
        return post

    @staticmethod
    def eliminar_post(post_id):
        PostForo.objects.get(id_post=post_id).delete()
        return True

    @staticmethod
    def obtener_total_posts_foro(foro_id):
        return PostForo.objects.filter(foro_id=foro_id).count()

    @staticmethod
    def obtener_post_por_id(post_id):
        return PostForo.objects.get(id_post=post_id)
