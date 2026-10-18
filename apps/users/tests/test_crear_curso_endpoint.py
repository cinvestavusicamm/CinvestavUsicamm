"""El endpoint de creacion de cursos: 400 con el campo, 403 sin rol, sin CSRF-exempt.

Cubre `views/generador_cursos/cursos.py:crear_curso_generador`, que es el
unico endpoint de creacion que la interfaz usa de verdad
(`static/js/generador/cursos.js` y `templates/generador_cursos/
generador_de_cursos.html`).

Lo que se fija aqui:

- sin rol o anonimo, no se crea nada;
- el rol se comprueba antes que el metodo HTTP, para que un usuario sin rol
  reciba su 403 y no un 405 por usar GET;
- el token CSRF es obligatorio de verdad, con la cookie como origen;
- un dato invalido es un 400 que dice el campo, y no un 500 con el error de la
  base dentro;
- un cuerpo que no es JSON es un 400, no un 500.

Todas las peticiones pasan por el cliente de Django con la cookie de sesion, no
por llamadas directas a la vista: asi se ejercita la cadena de decoradores
entera, que es donde estaban los problemas.
"""
import json

from django.test import Client, TestCase

from apps.users.config.constants import (
    ESTADO_BORRADOR,
    ESTADO_EN_REVISION,
    ROLE_ADMIN,
    ROLE_DOCENTE,
    ROLE_EVALUADOR,
    ROLE_GENERADOR,
)
from apps.users.models import Curso, Institucion, Rol, Usuario

URL = '/generador/api/crear-curso-generador/'


class _Base(TestCase):
    def setUp(self):
        self.institucion = Institucion.objects.create(
            nombre='Institucion de prueba', tipo='UNIVERSIDAD', activo=True,
        )
        self.roles = {
            nombre: Rol.objects.create(nombre_rol=nombre)
            for nombre in (ROLE_GENERADOR, ROLE_DOCENTE, ROLE_EVALUADOR, ROLE_ADMIN)
        }
        self.generador = self._usuario('Generador', 'gen', ROLE_GENERADOR)
        self.docente = self._usuario('Docente', 'doc', ROLE_DOCENTE)
        self.evaluador = self._usuario('Evaluador', 'eva', ROLE_EVALUADOR)
        self.admin = self._usuario('Admin', 'adm', ROLE_ADMIN)

        # Un cliente con la sesion ya iniciada, como el de la interfaz. El login
        # del proyecto es propio: se meten a mano las dos claves de sesion.
        #
        # enforce_csrf_checks va explicito porque el cliente de test de Django
        # omite la comprobacion de CSRF por defecto: sin esto, el test de "sin
        # token no crea" pasaria siempre y no probaria nada.
        self.cliente = Client(enforce_csrf_checks=True)
        self._iniciar(self.generador)
        # El token lo firma Django: no vale un string inventado en la cookie,
        # porque el middleware compara la firma y lo rechazaria. Se pide con un
        # GET real a la pagina del generador, que ya lo emite con
        # {% csrf_token %}.
        self._token_csrf()

    def _usuario(self, nombre, clave, rol):
        return Usuario.objects.create(
            nombre=nombre, apellido_paterno='Prueba',
            correo=f'{clave}@test.com', contrasena='x',
            curp=f'{clave.upper():<4}000000HDFMXN'[:18],
            rol=self.roles[rol], institucion=self.institucion,
        )

    def _iniciar(self, usuario):
        sesion = self.cliente.session
        sesion['usuario_id'] = usuario.id_usuario
        sesion['usuario_rol'] = usuario.rol.nombre_rol
        sesion.save()

    def _token_csrf(self, url='/sesion/'):
        """Coge una cookie csrftoken firmada por Django.

        Por defecto se pide en el login, que es accesible sin importar el rol.
        Importa por eso: el token va en la sesion, y estos tests cambian la
        sesion a DOCENTE, EVALUADOR y ADMIN, para los que la pagina del
        generador ya no responde. La pagina del generador tiene su propio test
        abajo, que es donde importa que emita el token.
        """
        respuesta = self.cliente.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('csrftoken', self.cliente.cookies, 'la pagina no fijo la cookie CSRF')
        return self.cliente.cookies['csrftoken'].value

    def _payload(self, **extra):
        datos = {
            'titulo': 'Curso de prueba',
            'descripcion': 'Una descripcion',
            'contenido': {'bloques': [{'titulo': 'tema'}]},
        }
        datos.update(extra)
        return datos

    def _con_token(self, payload):
        """Como lo hace el JS: cookie de sesion + X-CSRFToken."""
        return self.cliente.post(
            URL, data=json.dumps(payload), content_type='application/json',
            headers={'x-csrftoken': self._token_csrf()},
        )


class AutorizacionTests(_Base):
    def test_el_generador_crea_el_curso(self):
        respuesta = self._con_token(self._payload())
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()['success'])
        self.assertEqual(Curso.objects.count(), 1)

    def test_sin_rol_no_crea_y_devuelve_403(self):
        for rol, etiqueta in ((self.docente, 'DOCENTE'), (self.evaluador, 'EVALUADOR'),
                              (self.admin, 'ADMIN')):
            with self.subTest(rol=etiqueta):
                self._iniciar(rol)
                respuesta = self._con_token(self._payload())
                self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Curso.objects.count(), 0)

    def test_anonimo_no_crea_y_redirige(self):
        """Sin sesion, al login.

        Se manda token valido a proposito: si no, el 403 seria del middleware de
        CSRF y no probaria nada sobre la autorizacion.
        """
        self.cliente = Client(enforce_csrf_checks=True)
        token = self._token_csrf()
        respuesta = self.cliente.post(
            URL, data=json.dumps(self._payload()), content_type='application/json',
            headers={'x-csrftoken': token},
        )
        self.assertIn(respuesta.status_code, (302, 401))
        self.assertEqual(Curso.objects.count(), 0)

    def test_anonimo_sin_token_es_403_del_middleware(self):
        """El orden importa: CSRF va antes que la autorizacion."""
        self.cliente = Client(enforce_csrf_checks=True)
        respuesta = self.cliente.post(
            URL, data=json.dumps(self._payload()), content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Curso.objects.count(), 0)

    def test_un_usuario_inactivo_no_crea(self):
        """La sesion sobrevive a que la cuenta se desactive; requiere_rol no se la cree.

        Pide JSON como lo hace el JS, y entonces la respuesta es 401 en vez del
        redirect a la pagina de login, para que el navegador muestre el motivo
        en vez de un HTML inesperado.
        """
        self.generador.activo = False
        self.generador.save()

        respuesta = self.cliente.post(
            URL, data=json.dumps(self._payload()),
            content_type='application/json',
            headers={
                'x-csrftoken': self._token_csrf(),
                'x-requested-with': 'XMLHttpRequest',
            },
        )
        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(Curso.objects.count(), 0)

    def test_el_rol_se_comprueba_antes_que_el_metodo_http(self):
        """Sin rol, un GET da 403 y no 405.

        El orden de los decoradores importa: con requiere_rol debajo de
        require_http_methods se evalua primero.
        """
        self._iniciar(self.docente)
        respuesta = self.cliente.get(URL)
        self.assertEqual(respuesta.status_code, 403)

    def test_las_rutas_duplicadas_ya_no_existen(self):
        """No queda mas de un endpoint de creacion.

        Habia tres: /generador/api/crear/, /api/cursos/crear/ y
        /generador/api/crear-curso-generador/. Las dos primeras se retiraron
        al no tener consumidor. Este test es la red de seguridad para que no
        vuelvan a aparecer por el mismo camino.
        """
        for url in ('/generador/api/crear/', '/api/cursos/crear/',
                    '/api/cursos/listar/', '/generador/api/actualizar/1/'):
            with self.subTest(url=url):
                respuesta = self.cliente.get(url)
                self.assertEqual(respuesta.status_code, 404)


class CsrfTests(_Base):
    def test_sin_token_no_crea(self):
        """El csrf_exempt se quito: sin token, el middleware de Django rechaza."""
        respuesta = self.cliente.post(
            URL, data=json.dumps(self._payload()), content_type='application/json',
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Curso.objects.count(), 0)

    def test_con_un_token_inventado_no_crea(self):
        """La cookie vale, pero la cabecera no: el token tiene firma."""
        self._token_csrf()
        self.cliente.cookies['csrftoken'] = 'inventado'
        respuesta = self.cliente.post(
            URL, data=json.dumps(self._payload()), content_type='application/json',
            headers={'x-csrftoken': 'inventado'},
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Curso.objects.count(), 0)

    def test_la_plantilla_del_generador_emite_el_token(self):
        """Sin esto, el JS manda X-CSRFToken vacio y no habria forma de crear."""
        pagina = self.cliente.get('/generador/generador_de_cursos/')
        self.assertEqual(pagina.status_code, 200)
        # El token en el HTML, y ademas la cookie que el JS lee.
        self.assertContains(pagina, 'csrfmiddlewaretoken')
        self.assertIn('csrftoken', self.cliente.cookies)

    def test_la_plantilla_que_manda_el_js_es_la_misma(self):
        """El JS de cursos.js y la plantilla comparten el token; si una de las
        dos dejara de emitirlo, el guardado del curso dejaria de funcionar."""
        import pathlib

        from django.conf import settings

        raiz = pathlib.Path(settings.BASE_DIR)
        plantilla = (raiz / 'templates' / 'generador_cursos' / 'generador_de_cursos.html').read_text()
        self.assertIn('{% csrf_token %}', plantilla)
        js = (raiz / 'static' / 'js' / 'generador' / 'cursos.js').read_text()
        self.assertIn("getCookie('csrftoken')", js)


class DatosInvalidosTests(_Base):
    def test_sin_titulo_es_400_con_el_campo(self):
        respuesta = self._con_token(self._payload(titulo=''))
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['campo'], 'titulo')
        self.assertEqual(Curso.objects.count(), 0)

    def test_titulo_demasiado_largo_es_400(self):
        respuesta = self._con_token(self._payload(titulo='x' * 201))
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['campo'], 'titulo')

    def test_estado_desconocido_es_400_con_el_campo(self):
        respuesta = self._con_token(self._payload(estado='loquesea'))
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['campo'], 'estado')
        self.assertEqual(Curso.objects.count(), 0)

    def test_estado_valido_se_normaliza(self):
        respuesta = self._con_token(self._payload(estado='EnRevision'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Curso.objects.get().estado, ESTADO_EN_REVISION)

    def test_contenido_enorme_es_400_y_no_se_crea(self):
        # Entre 1 MB (el tope del servicio) y los 2,5 MB que Django admite por
        # defecto en una peticion, para que corte la validacion del servicio y
        # no el middleware.
        enorme = {'bloques': [{'texto': 'x' * 100_000} for _ in range(20)]}
        respuesta = self._con_token(self._payload(contenido=enorme))
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()['campo'], 'contenido')
        self.assertEqual(Curso.objects.count(), 0)

    def test_cuerpo_que_no_es_json_es_400(self):
        respuesta = self.cliente.post(
            URL, data='esto no es json', content_type='application/json',
            headers={'x-csrftoken': self._token_csrf()},
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('json', respuesta.json()['error'].lower())
        self.assertEqual(Curso.objects.count(), 0)

    def test_un_error_de_validacion_no_filtra_el_esquema_de_la_base(self):
        """Lo que se ve en el 400 es un mensaje, no una consulta SQL."""
        respuesta = self._con_token(self._payload(titulo=''))
        cuerpo = respuesta.content.decode()
        for filtrado in ('SELECT', 'INSERT', 'NOT NULL', 'IntegrityError',
                         'Traceback', 'cursos_', 'sqlite3', 'postgres'):
            self.assertNotIn(filtrado, cuerpo)


class LoQueSeGuardaTests(_Base):
    def test_el_docente_es_el_de_la_sesion(self):
        """No request.user: el login es por sesion propia y .id no existe."""
        respuesta = self._con_token(self._payload())
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Curso.objects.get().docente_id, self.generador.pk)

    def test_nace_en_borrador_aunque_no_venga_estado(self):
        self._con_token(self._payload())
        self.assertEqual(Curso.objects.get().estado, ESTADO_BORRADOR)

    def test_el_contenido_se_guarda(self):
        contenido = {'bloques': [{'titulo': 'tema', 'contenido': 'texto'}]}
        self._con_token(self._payload(contenido=contenido))
        self.assertEqual(Curso.objects.get().contenido_json, contenido)

    def test_generado_con_ia_se_respeta(self):
        self._con_token(self._payload(generado_con_ia=True))
        self.assertTrue(Curso.objects.get().generado_con_ia)

    def test_sin_estado_nace_en_borrador(self):
        """El default del endpoint y del servicio es Borrador.

        Este endpoint guarda lo que le pidan, incluido Aprobado: quien decide
        si un curso pasa a aprobado es el flujo de revision, no esta pantalla.
        La regla de que lo generado por IA no nace aprobado se aplica mas
        arriba, en el punto 5, cuando se conecte el modelo de verdad.
        """
        self._con_token(self._payload())
        self.assertEqual(Curso.objects.get().estado, ESTADO_BORRADOR)

    def test_el_estado_pedido_se_guarda(self):
        self._con_token(self._payload(estado=ESTADO_EN_REVISION))
        self.assertEqual(Curso.objects.get().estado, ESTADO_EN_REVISION)

class GuardadoExtremoAExtremoTests(_Base):
    """El flujo completo del boton Guardar, tal como lo llama la plantilla.

    No es una prueba de la vista por separado: replica el payload exacto que
    construye `guardarCurso()` en `generador_de_cursos.html` y lo manda por la
    URL exacta que esa funcion escribe, con la cabecera CSRF que manda su
    `fetch`. Si alguien cambia una de esas tres cosas (payload, URL o cabecera)
    y no la otra, este test cae.

    Ver tambien `test_la_plantilla_que_manda_el_js_es_la_misma`, que comprueba
    que la plantilla y el JS comparten el token.
    """

    # Copiado de recolectarContenidoCurso() de generador_de_cursos.html. Las
    # tres secciones fijas (presentacion, modulos, examen) y el orden de sus
    # campos importan, porque es lo que la vista guarda tal cual en
    # contenido_json y lo que luego espera ver quien renderiza.
    def _payload_de_guardarCurso(self, estado='Borrador'):
        return {
            'titulo': 'Algebra lineal',
            'descripcion': 'Curso de introduccion',
            'contenido': {
                'presentacion': {'titulo': 'Algebra lineal',
                                 'descripcion': 'Curso de introduccion',
                                 'duracion': '12 horas'},
                'modulos': [
                    {'titulo': 'Sistemas de ecuaciones', 'items': [{'tipo': 'video'}]},
                    {'titulo': 'Matrices', 'items': [{'tipo': 'quiz', 'preguntas': [
                        {'pregunta': 'Que es una matriz?',
                         'opciones': ['tabla', 'nota'],
                         'correcta': 'tabla'}]}]},
                    {'titulo': 'Determinantes', 'items': [{'tipo': 'video'}]},
                ],
                'examen': {'preguntas': []},
            },
            'estado': estado,
            'generado_con_ia': True,
        }

    def test_la_url_del_js_es_la_que_se_prueba(self):
        """El JS no puede cambiar de endpoint por su cuenta.

        La URL del test esta escrita a mano mas arriba; esta comprueba contra el
        texto real de la plantilla, que es donde el navegador la pone. Si se
        retira la vista o se mueve la ruta, los dos lados del fetch caen
        juntos.
        """
        import pathlib

        from django.conf import settings

        plantilla = (
            pathlib.Path(settings.BASE_DIR)
            / 'templates' / 'generador_cursos' / 'generador_de_cursos.html'
        ).read_text()
        self.assertIn("'/generador/api/crear-curso-generador/'", plantilla)
        self.assertEqual(URL, '/generador/api/crear-curso-generador/')

    def test_guardar_borrador_guarda_con_docente_y_estado(self):
        """El boton Guardar, la rama de creacion (cursoActual.id nulo)."""
        respuesta = self._con_token(self._payload_de_guardarCurso('Borrador'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()['success'])

        self.assertEqual(Curso.objects.count(), 1)
        curso = Curso.objects.get()
        self.assertEqual(curso.id_curso, respuesta.json()['curso_id'])
        # El docente es el de la sesion, que es lo que se pedia: el login es
        # propio y request.user.id no existe.
        self.assertEqual(curso.docente_id, self.generador.pk)
        self.assertEqual(curso.estado, ESTADO_BORRADOR)
        self.assertEqual(curso.titulo, 'Algebra lineal')
        self.assertTrue(curso.generado_con_ia)

    def test_subir_a_revision_guarda_en_revision(self):
        """`subirAAprobacion()` llama a guardarCurso('En_Revisión')."""
        respuesta = self._con_token(self._payload_de_guardarCurso(ESTADO_EN_REVISION))

        self.assertEqual(respuesta.status_code, 200)
        curso = Curso.objects.get()
        self.assertEqual(curso.estado, ESTADO_EN_REVISION)
        self.assertEqual(curso.docente_id, self.generador.pk)

    def test_el_contenido_llega_igual_que_lo_que_manda_el_js(self):
        """Se guarda la estructura de tres secciones, no una version aplanada."""
        payload = self._payload_de_guardarCurso()
        self._con_token(payload)

        curso = Curso.objects.get()
        self.assertEqual(curso.contenido_json, payload['contenido'])
        self.assertEqual(list(curso.contenido_json),
                         ['presentacion', 'modulos', 'examen'])
        self.assertEqual(len(curso.contenido_json['modulos']), 3)
        self.assertEqual(
            curso.contenido_json['modulos'][1]['items'][0]['preguntas'][0]['correcta'],
            'tabla',
        )
        self.assertEqual(curso.contenido_json['examen']['preguntas'], [])
