import datetime
from io import StringIO

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.config.constants import (
    ESTADO_BORRADOR,
    ESTADO_EN_REVISION,
    ROLE_ADMIN,
    ROLE_DOCENTE,
)
from apps.users.models import BitacoraEvento, Curso, Institucion, Rol, Usuario

_contador = [0]


class AdminCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.institucion = Institucion.objects.create(
            nombre='Institucion de prueba',
            tipo='UNIVERSIDAD',
            activo=True,
        )
        self.rol_admin = Rol.objects.create(nombre_rol=ROLE_ADMIN)
        self.rol_docente = Rol.objects.create(nombre_rol=ROLE_DOCENTE)
        self.rol_custom = Rol.objects.create(nombre_rol='COORDINADOR')

        self.admin = self._crear_usuario('Admin', self.rol_admin)
        self.docente = self._crear_usuario('Docente', self.rol_docente)

        self.curso = Curso.objects.create(
            titulo='Curso existente',
            descripcion='Curso de prueba',
            docente=self.docente,
            estado=ESTADO_BORRADOR,
        )

    def _crear_usuario(self, nombre, rol):
        _contador[0] += 1
        numero = _contador[0]
        return Usuario.objects.create(
            nombre=nombre,
            apellido_paterno='Prueba',
            correo=f'admincrud{numero}@test.com',
            curp=f'CRUD{numero:02d}000000AAA0',
            contrasena='x',
            rol=rol,
            institucion=self.institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )

    def _login(self, usuario=None):
        usuario = usuario or self.admin
        session = self.client.session
        session['usuario_id'] = usuario.id_usuario
        session['usuario_rol'] = usuario.rol.nombre_rol
        session['usuario_nombre'] = usuario.nombre_completo
        session.save()

    def test_admin_puede_ver_listado_de_cursos(self):
        self._login()

        respuesta = self.client.get(reverse('administrador:cursos'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Curso existente')
        self.assertContains(respuesta, 'Nuevo curso')

    def test_admin_puede_ver_listado_de_roles(self):
        self._login()

        respuesta = self.client.get(reverse('administrador:roles'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'COORDINADOR')
        self.assertContains(respuesta, 'Sistema')

    def test_docente_no_puede_entrar_al_crud(self):
        self._login(self.docente)

        self.assertEqual(self.client.get(reverse('administrador:cursos')).status_code, 403)
        self.assertEqual(self.client.get(reverse('administrador:roles')).status_code, 403)

    def test_crear_curso(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:curso_crear'),
            {
                'titulo': 'Curso nuevo',
                'descripcion': 'Descripcion nueva',
                'docente': self.docente.id_usuario,
                'estado': ESTADO_EN_REVISION,
                'generado_con_ia': 'on',
            },
        )

        self.assertRedirects(respuesta, reverse('administrador:cursos'))
        curso = Curso.objects.get(titulo='Curso nuevo')
        self.assertEqual(curso.estado, ESTADO_EN_REVISION)
        self.assertTrue(curso.generado_con_ia)
        self.assertEqual(curso.docente_id, self.docente.id_usuario)

    def test_crear_curso_sin_titulo_no_lo_guarda(self):
        self._login()
        antes = Curso.objects.count()

        respuesta = self.client.post(
            reverse('administrador:curso_crear'),
            {
                'titulo': '',
                'docente': self.docente.id_usuario,
                'estado': ESTADO_BORRADOR,
            },
            follow=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Curso.objects.count(), antes)
        self.assertContains(respuesta, 'El titulo del curso no puede estar vacio')

    def test_editar_curso(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:curso_editar', kwargs={'id': self.curso.id_curso}),
            {
                'titulo': 'Curso actualizado',
                'descripcion': 'Nueva descripcion',
                'docente': self.admin.id_usuario,
                'estado': ESTADO_EN_REVISION,
                'generado_con_ia': 'on',
            },
        )

        self.assertRedirects(respuesta, reverse('administrador:cursos'))
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.titulo, 'Curso actualizado')
        self.assertEqual(self.curso.estado, ESTADO_EN_REVISION)
        self.assertEqual(self.curso.docente_id, self.admin.id_usuario)
        self.assertTrue(self.curso.generado_con_ia)

    def test_eliminar_curso(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:curso_eliminar', kwargs={'id': self.curso.id_curso})
        )

        self.assertRedirects(respuesta, reverse('administrador:cursos'))
        self.assertFalse(Curso.objects.filter(id_curso=self.curso.id_curso).exists())

    def test_crear_rol(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_crear'),
            {'nombre_rol': 'nuevo_rol'},
        )

        self.assertRedirects(respuesta, reverse('administrador:roles'))
        self.assertTrue(Rol.objects.filter(nombre_rol='NUEVO_ROL').exists())

    def test_no_crear_rol_duplicado(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_crear'),
            {'nombre_rol': 'coordinador'},
            follow=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Rol.objects.filter(nombre_rol__iexact='COORDINADOR').count(), 1)
        self.assertContains(respuesta, 'Ya existe un rol con ese nombre')

    def test_no_crear_rol_vacio(self):
        self._login()
        antes = Rol.objects.count()

        respuesta = self.client.post(
            reverse('administrador:rol_crear'),
            {'nombre_rol': '   '},
            follow=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Rol.objects.count(), antes)
        self.assertContains(respuesta, 'El nombre del rol es obligatorio')

    def test_editar_rol_personalizado(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_editar', kwargs={'id': self.rol_custom.id_rol}),
            {'nombre_rol': 'coordinador_general'},
        )

        self.assertRedirects(respuesta, reverse('administrador:roles'))
        self.rol_custom.refresh_from_db()
        self.assertEqual(self.rol_custom.nombre_rol, 'COORDINADOR_GENERAL')

    def test_no_renombrar_rol_del_sistema(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_editar', kwargs={'id': self.rol_admin.id_rol}),
            {'nombre_rol': 'OTRO'},
            follow=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.rol_admin.refresh_from_db()
        self.assertEqual(self.rol_admin.nombre_rol, ROLE_ADMIN)
        self.assertContains(respuesta, 'Los roles del sistema no se pueden renombrar')

    def test_no_eliminar_rol_del_sistema(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_eliminar', kwargs={'id': self.rol_admin.id_rol})
        )

        self.assertRedirects(respuesta, reverse('administrador:roles'))
        self.assertTrue(Rol.objects.filter(id_rol=self.rol_admin.id_rol).exists())

    def test_no_eliminar_rol_con_usuarios(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_eliminar', kwargs={'id': self.rol_docente.id_rol})
        )

        self.assertRedirects(respuesta, reverse('administrador:roles'))
        self.assertTrue(Rol.objects.filter(id_rol=self.rol_docente.id_rol).exists())

    def test_eliminar_rol_personalizado_sin_usuarios(self):
        self._login()

        respuesta = self.client.post(
            reverse('administrador:rol_eliminar', kwargs={'id': self.rol_custom.id_rol})
        )

        self.assertRedirects(respuesta, reverse('administrador:roles'))
        self.assertFalse(Rol.objects.filter(id_rol=self.rol_custom.id_rol).exists())

    def test_crud_de_curso_registra_bitacora(self):
        self._login()

        self.client.post(
            reverse('administrador:curso_crear'),
            {
                'titulo': 'Curso con bitacora',
                'docente': self.docente.id_usuario,
                'estado': ESTADO_BORRADOR,
            },
        )
        self.assertTrue(
            BitacoraEvento.objects.filter(tipo_evento='CURSO_CREADO').exists()
        )

        curso = Curso.objects.get(titulo='Curso con bitacora')
        self.client.post(
            reverse('administrador:curso_eliminar', kwargs={'id': curso.id_curso})
        )
        self.assertTrue(
            BitacoraEvento.objects.filter(tipo_evento='CURSO_ELIMINADO').exists()
        )

    def test_create_initial_data_es_idempotente(self):
        call_command('create_initial_data', stdout=StringIO())
        call_command('create_initial_data', stdout=StringIO())

        self.assertEqual(Rol.objects.filter(nombre_rol=ROLE_ADMIN).count(), 1)
        self.assertEqual(Rol.objects.filter(nombre_rol='EVALUADOR').count(), 1)
        self.assertEqual(
            Institucion.objects.filter(nombre='Institución de Prueba').count(), 1
        )
        self.assertEqual(Curso.objects.filter(titulo='Curso de Prueba').count(), 1)
        self.assertEqual(
            Usuario.objects.filter(curp='ADMI900101HDFRRN01').count(), 1
        )
