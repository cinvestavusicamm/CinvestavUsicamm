"""
La clave compartida con el microservicio de IA sale del entorno, no del codigo.

Antes `apps/users/api/agente.py` traia la cadena de la clave escrita en el fuente:
el repositorio entero llevaba una credencial de servicio versionada y rotarla
exigia editar codigo. Aqui se fija el contrato nuevo:

- sin INTERNAL_SERVICE_KEY, /agente-ajax/ falla con un error que nombra la variable
- con ella, la clave viaja en X-Internal-Service-Key
- en produccion, core.settings.prov se niega a arrancar si falta

Este test no hace red: requests.post va mockeado. Lo que se comprueba es la
configuracion, no el microservicio.
"""
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, Client, override_settings
import datetime

from apps.users.api.agente import clave_del_servicio
from apps.users.config.constants import ROLE_ADMIN
from apps.users.models import Usuario, Rol, Institucion


CLAVE = 'clave-de-prueba-no-es-la-real'
RUTA = '/agente-ajax/'


class ClaveDelServicioTests(TestCase):
    """La funcion que resuelve la clave."""

    @override_settings(INTERNAL_SERVICE_KEY=CLAVE)
    def test_devuelve_la_clave_del_entorno(self):
        self.assertEqual(clave_del_servicio(), CLAVE)

    @override_settings(INTERNAL_SERVICE_KEY='')
    def test_sin_clave_falla_diciendo_que_falta(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            clave_del_servicio()
        mensaje = str(ctx.exception)
        # El mensaje tiene que ser accionable: no basta con "error de
        # configuracion", hay que decir que variable falta y donde se define.
        self.assertIn('INTERNAL_SERVICE_KEY', mensaje)
        self.assertIn('.env.example', mensaje)

    @override_settings(INTERNAL_SERVICE_KEY='   ')
    def test_espacios_no_cuentan_como_clave(self):
        """Una clave de espacios passesaria el if not clave y llegaria al
        microservicio como algo que este rechazo, con un 403 dificil de leer."""
        with self.assertRaises(ImproperlyConfigured):
            clave_del_servicio()

    def test_el_setting_existe_y_no_trae_credencial(self):
        """Guardia contra que alguien vuelva a poner un valor de repuesto."""
        self.assertTrue(hasattr(settings, 'INTERNAL_SERVICE_KEY'))
        self.assertNotIn('prod', (settings.INTERNAL_SERVICE_KEY or '').lower())

    def test_ninguna_fuente_de_python_tiene_la_clave_escrita(self):
        """La credencial no debe volver a aparecer en ningun proyecto.

        Es la parte que un revisor no ve: el grep del literal completo.

        Abarca tambien ``ia_service_core``. Antes esa copia vivia en su
        ``security.py`` y el test se limitaba a ``apps/`` y ``core/`` con un
        comentario explicando por que; desde que el nombre canonico esta
        unificado (DEUDA-8) el microservicio tambien tiene que estar limpio.
        """
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR)
        marcadores = ('clave_estricta', 'cambiar_en_prod')
        ofensores = []
        for sub in ('apps', 'core', 'ia_service_core'):
            for ruta in (raiz / sub).rglob('*.py'):
                # Se excluye la suite: este fichero nombra los marcadores para
                # poder buscarlos, asi que se encontraria a si mismo.
                if 'tests' in ruta.parts or '__pycache__' in ruta.parts:
                    continue
                texto = ruta.read_text(errors='ignore')
                if any(m in texto for m in marcadores):
                    ofensores.append(str(ruta.relative_to(raiz)))

        self.assertEqual(
            ofensores, [],
            f'credencial de servicio escrita en codigo: {ofensores}',
        )


class AgenteConClaveTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        institucion, _ = Institucion.objects.get_or_create(
            nombre='Institucion de prueba',
            defaults={'tipo': 'UNIVERSIDAD', 'activo': True},
        )
        rol, _ = Rol.objects.get_or_create(nombre_rol=ROLE_ADMIN)
        usuario = Usuario.objects.create(
            nombre='Admin',
            apellido_paterno='Clave',
            correo='clave@test.com',
            curp='CLAVE000000AAA0001',
            contrasena='x',
            rol=rol,
            institucion=institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )
        session = self.client.session
        session['usuario_id'] = usuario.id_usuario
        session['usuario_rol'] = ROLE_ADMIN
        session.save()

        mock_post = patch('apps.users.api.agente.requests.post').start()
        self.addCleanup(patch.stopall)
        self.mock_post = mock_post
        self.mock_post.return_value.json.return_value = {'response': 'Respuesta'}
        self.mock_post.return_value.raise_for_status = lambda: None


@override_settings(INTERNAL_SERVICE_KEY=CLAVE)
class ConClaveDefinidaTests(AgenteConClaveTestBase):

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_la_clave_viaja_en_la_cabecera(self, mock_decidir):
        mock_decidir.return_value = 'agente'

        response = self.client.post(RUTA, {'pregunta': 'hola'})

        self.assertEqual(response.status_code, 200)
        self.mock_post.assert_called_once()
        cabeceras = self.mock_post.call_args.kwargs['headers']
        self.assertEqual(cabeceras['X-Internal-Service-Key'], CLAVE)

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_la_clave_no_aparece_en_el_cuerpo_ni_en_la_url(self, mock_decidir):
        """Va solo en la cabecera. Mandarla tambien en el body la escribiria en
        los logs del microservicio, que es justo donde no debe estar."""
        mock_decidir.return_value = 'agente'

        self.client.post(RUTA, {'pregunta': 'hola'})

        llamada = self.mock_post.call_args
        cuerpo = llamada.kwargs['json']
        url = llamada.args[0] if llamada.args else ''
        self.assertNotIn(CLAVE, str(cuerpo))
        self.assertNotIn(CLAVE, str(url))


@override_settings(INTERNAL_SERVICE_KEY='')
class SinClaveDefinidaTests(AgenteConClaveTestBase):

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_falla_en_vez_de_mandar_la_peticion(self, mock_decidir):
        """Lo importante: sin clave no se sale a la red. Si se mandara, el
        microservicio contestaria 403 y el usuario veria un error generico
        en vez de un despliegue mal configurado."""
        mock_decidir.return_value = 'agente'

        with self.assertRaises(ImproperlyConfigured) as ctx:
            self.client.post(RUTA, {'pregunta': 'hola'})

        self.assertIn('INTERNAL_SERVICE_KEY', str(ctx.exception))
        self.mock_post.assert_not_called()

    @patch('apps.users.services.router_service.RouterService.decidir')
    def test_el_error_no_se_disfraza_de_fallo_del_microservicio(self, mock_decidir):
        """El except que envuelve la llamada se come cualquier Exception y
        devuelve un 500 de 'ocurrio un error inesperado'. Si la clave se
        resolvera dentro de ese bloque, el mensaje claro se perderia."""
        mock_decidir.return_value = 'agente'

        with self.assertRaises(ImproperlyConfigured):
            self.client.post(RUTA, {'pregunta': 'hola'})


class AjustesDePlantillaTest(TestCase):
    """El otro lado del contrato: /agente-ajax/ es el unico que usa la clave."""

    def test_agente_es_el_unico_que_consulta_el_servicio_de_ia(self):
        """Las tres vistas de ms_ai_agent_service no mandan X-Internal-Service-Key,
        asi que a 8107 no les sirve INTERNAL_SERVICE_KEY: van a otro servicio con
        otro esquema de autenticacion. Por eso este arreglo no las toca."""
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR) / 'apps' / 'users' / 'views'
        con_clave = sorted(
            ruta.name
            for ruta in raiz.glob('*.py')
            if 'X-Internal-Service-Key' in ruta.read_text(errors='ignore')
        )

        self.assertEqual(con_clave, [])


class ProduccionExigeClaveTests(TestCase):
    """core.settings.prov comprueba la clave al arrancar.

    No se puede importar prov en el proceso de test porque el resto de ajustes
    de produccion tambien exigirian variables. Se comprueba lo que importa:
    que el ajuste existe en base con default vacio -- lo que permite que el error
    sea al usar el endpoint y no al arrancar cualquier comando -- y que prov
    tiene la comprobacion.
    """
    def test_base_deja_la_clave_vacia_y_no_una_credencial(self):
        # Se mira el fichero y no settings.INTERNAL_SERVICE_KEY: dev carga el
        # .env del desarrollador, asi que la clave del entorno no dice nada
        # sobre cual es el default del proyecto.
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR)
        base = (raiz / 'core' / 'settings' / 'base.py').read_text()
        self.assertIn("INTERNAL_SERVICE_KEY = config('INTERNAL_SERVICE_KEY', default='')", base)

    def test_prov_tiene_la_comprobacion(self):
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR)
        prov = (raiz / 'core' / 'settings' / 'prov.py').read_text()
        self.assertIn('INTERNAL_SERVICE_KEY', prov)
        self.assertIn('ImproperlyConfigured', prov)


class UnSoloNombreDeClaveTests(TestCase):
    """Django y el microservicio tienen que leer la misma variable.

    Es la parte que se rompio en silencio durante meses: `microAI` no la
    definia nadie, `MICROSERVICE_SECRET` no lo leia nadie, y la comunicacion
    funcionaba solo porque la misma cadena estaba escrita a mano en dos
    ficheros. Estos tests fallan si alguien vuelve a inventarse un nombre.
    """
    COMPOSES = (
        'docker-compose.yml',
        'docker-compose.prod.yml',
        'infrastructure/docker-compose.yml',
        'ia_service_core/docker-compose.yml',
    )

    def _raiz(self):
        import pathlib

        return pathlib.Path(settings.BASE_DIR)

    def _microservicio_actualiza_la_clave(self, entorno, expression):
        """Ejecuta el microservicio en un subproceso y devuelve su salida.

        Un subproceso y no un import: la guarda de `security.py` es de nivel de
        modulo, asi que importarlo aqui contaminaria el proceso de test, y
        ademas el arranque real es justo lo que hay que comprobar.
        """
        import subprocess
        import sys
        import textwrap

        raiz = self._raiz()
        guion = textwrap.dedent(
            f"""
            import sys
            sys.path.insert(0, {str(raiz / 'ia_service_core' / 'src')!r})
            from infrastructure.api.security import INTERNAL_KEY
            print({expression})
            """
        )
        proceso = subprocess.run(
            [sys.executable, '-c', guion],
            capture_output=True,
            text=True,
            env=entorno,
            timeout=60,
        )
        return proceso

    def test_el_microservicio_lee_la_variable_canonica(self):
        import importlib.util
        import os

        if importlib.util.find_spec('fastapi') is None:
            self.skipTest('fastapi no esta instalado en este interprete')

        ruta = self._raiz() / 'ia_service_core' / 'src' / 'infrastructure' / 'api' / 'security.py'
        texto = ruta.read_text()
        self.assertIn('INTERNAL_SERVICE_KEY', texto)

        # Con la variable definida, lo que lee el microservicio es lo mismo que
        # lee Django. Es el contrato entero de la clave en una linea.
        entorno = {k: v for k, v in os.environ.items()}
        entorno['INTERNAL_SERVICE_KEY'] = 'clave-compartida-de-prueba'
        with override_settings(INTERNAL_SERVICE_KEY='clave-compartida-de-prueba'):
            proceso = self._microservicio_actualiza_la_clave(
                entorno, 'INTERNAL_KEY == "clave-compartida-de-prueba"'
            )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn('True', proceso.stdout)

    def test_ningun_python_lee_los_nombres_viejos_de_la_clave(self):
        """Que el nombre viejo no vuelva a ser el que se consulta.

        Importa mas leer que mencionar: los comentarios que explican la
        historia si pueden nombrar `microAI`, lo que no puede es un
        `getenv("microAI")`, porque eso reabre el fallo en silencio.
        """
        import pathlib
        import re

        raiz = self._raiz()
        lectura_vieja = re.compile(r"""(?:getenv|environ(?:\.get)?)\(\s*["'](?:microAI|MICROSERVICE_SECRET)["']""")
        ofensores = []
        for sub in ('apps', 'core', 'ia_service_core'):
            for ruta in (raiz / sub).rglob('*.py'):
                if 'tests' in ruta.parts or '__pycache__' in ruta.parts:
                    continue
                if lectura_vieja.search(ruta.read_text(errors='ignore')):
                    ofensores.append(str(ruta.relative_to(raiz)))
        self.assertEqual(ofensores, [], f'ainda se lee el nombre viejo en: {ofensores}')

    def test_el_microservicio_se_niega_a_arrancar_sin_clave(self):
        import importlib.util
        import os

        if importlib.util.find_spec('fastapi') is None:
            self.skipTest('fastapi no esta instalado en este interprete')

        entorno = {k: v for k, v in os.environ.items()}
        # Se barren los tres nombres historicos: ninguno debe resucitar la
        # arranque con una clave cualquiera.
        for nombre in ('INTERNAL_SERVICE_KEY', 'microAI', 'MICROSERVICE_SECRET'):
            entorno.pop(nombre, None)
        proceso = self._microservicio_actualiza_la_clave(entorno, 'INTERNAL_KEY')
        self.assertNotEqual(proceso.returncode, 0, 'arranco sin clave definida')
        self.assertIn('INTERNAL_SERVICE_KEY', proceso.stderr)
        self.assertIn('RuntimeError', proceso.stderr)

    def test_ningun_compose_asigna_los_nombres_viejos(self):
        """Que ningun compose vuelva a *pasar* una clave por otro nombre.

        Se buscan las asignaciones, no la palabra: un comentario que explica
        que antes ponia MICROSERVICE_SECRET es util, una linea que lo pone en el
        entorno es el bug.
        """
        import re

        raiz = self._raiz()
        asigna_viejo = re.compile(r'MICROSERVICE_SECRET\s*[:=]|(?<![\w-])microAI\s*[:=]')
        ofensores = []
        for nombre in self.COMPOSES:
            ruta = raiz / nombre
            self.assertTrue(ruta.exists(), nombre)
            texto = ruta.read_text()
            for linea in texto.splitlines():
                if asigna_viejo.search(linea) and not linea.lstrip().startswith('#'):
                    ofensores.append(f'{nombre}: {linea.strip()}')
            # Ademas, ninguno debe volver a traer una credencial escrita.
            if 'clave_estricta' in texto or 'super_secreto_interno' in texto:
                ofensores.append(f'{nombre}: credencial escrita')
        self.assertEqual(ofensores, [])

    def test_los_composes_exigen_la_variable_en_vez_de_darla_por_defecto(self):
        """${VAR:?} corta el arranque; ${VAR:-defecto} lo deja arrancar roto.

        Se busca la interpolacion y no el `INTERNAL_SERVICE_KEY:` literal porque
        los compose usan los dos estilos de YAML: mapeo (`clave: ${...}`) en
        infrastructure/ e ia_service_core/, y lista (`- clave=${...}`) en los
        de la raiz.
        """
        for nombre in self.COMPOSES:
            texto = (self._raiz() / nombre).read_text()
            self.assertIn(
                '${INTERNAL_SERVICE_KEY:?',
                texto,
                nombre + ' no pasa la clave al contenedor con ${INTERNAL_SERVICE_KEY:?}',
            )
            self.assertNotIn(
                '${INTERNAL_SERVICE_KEY:-',
                texto,
                nombre + ' le pone un valor por defecto a la clave',
            )

    def test_django_recibe_la_clave_que_manda_al_microservicio(self):
        """El servicio django de los compose raiz y prod tambien la recibe.

        Sin esto, `docker compose up -d` levanta Django sin clave y
        /agente-ajax/ solo falla cuando alguien lo usa.
        """
        for nombre in ('docker-compose.yml', 'docker-compose.prod.yml'):
            texto = (self._raiz() / nombre).read_text()
            self.assertIn('${INTERNAL_SERVICE_KEY:?', texto, nombre)

    def test_el_env_example_avis_de_generar_una_clave_nueva(self):
        """La anterior esta en el historial de git: hay que rotarla."""
        ejemplo = (self._raiz() / '.env.example').read_text()
        self.assertIn('token_urlsafe', ejemplo)
        self.assertIn('historial', ejemplo)
        # La plantilla sigue dejando la clave en blanco: un valor de ejemplo
        # seria una credencial mas en el repositorio.
        self.assertTrue(
            ejemplo.rstrip().endswith('INTERNAL_SERVICE_KEY='),
            'la ultima linea de .env.example deberia ser INTERNAL_SERVICE_KEY= vacio',
        )