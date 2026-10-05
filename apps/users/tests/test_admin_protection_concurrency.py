"""
Comprobacion de concurrencia de la proteccion del ultimo ADMIN activo.

Este modulo NO se puede verificar con SQLite: Django ignora
select_for_update en ese backend, asi que los tests de
test_admin_protection.py prueban la logica y el rollback, pero no el
bloqueo. Aqui lo que se prueba es el bloqueo de verdad, y por eso solo
corre en PostgreSQL.

Para ejecutarlo:

    docker compose up -d postgres
    docker compose exec postgres pg_isready -U user -d cinvestav_db

    DJANGO_SETTINGS_MODULE=core.settings.dev \\
    DATABASE_URL=postgresql://user:password@localhost:5432/cinvestav_db \\
    ./venv/bin/python manage.py test apps.users.tests.test_admin_protection_concurrency \\
    --keepdb

Se salta entero si la base no es PostgreSQL. Una ejecion en verde no es
prueba de que no haya carrera: para eso hay que repetirlo, y lo que
demuestra de verdad es que el segundo hilo RECHAZA en lugar de dejar el
sistema sin ADMIN, que es lo que pasaria sin select_for_update.
"""
import datetime
import threading

from django.db import close_old_connections, connection
from django.test import TransactionTestCase

from apps.users.config.constants import ROLE_ADMIN
from apps.users.models import Institucion, Rol, Usuario
from apps.users.services.user_service import OperacionRechazada, UserService


class ConcurrenciaDeUltimoAdminTests(TransactionTestCase):
    # TransactionTestCase y no TestCase: hace falta que cada transaccion
    # cierre de verdad para que el bloqueo de fila se tome y se libere.
    # TestCase lo envuelve todo en un atomic que no confirma nada.

    def setUp(self):
        if connection.vendor != "postgresql":
            self.skipTest(
                "select_for_update no tiene efecto en "
                f"{connection.vendor}; requiere PostgreSQL"
            )

        self.institucion = Institucion.objects.create(
            nombre="Concurrencia", tipo="UNIVERSIDAD", activo=True
        )
        self.rol_admin = Rol.objects.create(nombre_rol=ROLE_ADMIN)

        self.admin_a = self._crear_admin("A")
        self.admin_b = self._crear_admin("B")

    def _crear_admin(self, letra):
        return Usuario.objects.create(
            nombre="Admin",
            apellido_paterno=letra,
            correo=f"concurrencia{letra.lower()}@test.com",
            curp=f"CONC{letra}00000000AAA0",
            contrasena="x",
            rol=self.rol_admin,
            institucion=self.institucion,
            activo=True,
            fecha_registro=datetime.datetime.now(),
        )

    def _desactivar_en_hilo(self, usuario_id, barrera, resultados, posicion):
        """Cada hilo necesita su propia conexion: Django no comparte
        conexiones entre hilos y una transaccion abierta en el hilo principal
        no protegeria nada aqui."""
        close_old_connections()
        try:
            # La barrera hace que los dos hilos lleguen juntos al servicio.
            barrera.wait(timeout=10)
            UserService.alternar_activo(usuario_id, actor_id=None)
            resultados[posicion] = "ok"
        except OperacionRechazada:
            resultados[posicion] = "rechazado"
        except Exception as exc:  # pragma: no cover - solo diagnostico
            resultados[posicion] = f"error: {exc}"
        finally:
            connection.close()

    def test_dos_desactivaciones_simultaneas_no_dejan_el_sistema_sin_admin(self):
        """Con dos ADMIN activos, cada hilo intenta apagar al otro.

        Sin select_for_update los dos leerian "hay dos" y los dos
        confirmarian, dejando cero ADMIN activos. Con el bloqueo, el
        segundo espera, vuelve a leer y encuentra que solo queda uno.
        """
        barrera = threading.Barrier(2)
        resultados = [None, None]

        hilos = [
            threading.Thread(
                target=self._desactivar_en_hilo,
                args=(self.admin_b.id_usuario, barrera, resultados, 0),
            ),
            threading.Thread(
                target=self._desactivar_en_hilo,
                args=(self.admin_a.id_usuario, barrera, resultados, 1),
            ),
        ]

        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join(timeout=30)

        activos = Usuario.objects.filter(
            activo=True, rol__nombre_rol=ROLE_ADMIN
        ).count()

        self.assertEqual(
            activos,
            1,
            f"el sistema quedo con {activos} ADMIN activos "
            f"(resultados: {resultados})",
        )
        self.assertIn(
            "rechazado",
            resultados,
            f"ninguno de los dos hilos fue rechazado: {resultados}",
        )