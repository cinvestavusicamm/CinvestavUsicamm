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
        """La credencial no debe volver a aparecer en el proyecto Django.

        Es la parte que un revisor no ve: el grep del literal completo.

        El alcance es apps/ y core/ a proposito. El microservicio de IA es otro
        proyecto y su copia de la credencial sigue ahi, registrada en DEUDA-8
        con el arreglo pendiente; si este test la cubriera, fallaria el dia
        que se arregle alli, que es senal de que el test se quedo viejo.
        """
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR)
        marcadores = ('clave_estricta', 'cambiar_en_prod')
        ofensores = []
        for sub in ('apps', 'core'):
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
        self.assertEqual(settings.INTERNAL_SERVICE_KEY, '')

    def test_prov_tiene_la_comprobacion(self):
        import pathlib

        raiz = pathlib.Path(settings.BASE_DIR)
        prov = (raiz / 'core' / 'settings' / 'prov.py').read_text()
        self.assertIn('INTERNAL_SERVICE_KEY', prov)
        self.assertIn('ImproperlyConfigured', prov)