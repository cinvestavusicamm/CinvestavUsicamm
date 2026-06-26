from django.test import TestCase, Client


class FlujoCompletoTest(TestCase):

    def setUp(self):

        self.client = Client()

        # 🔥 Simular sesión
        session = self.client.session
        session['usuario_id'] = 1
        session.save()

    # ✅ TEST AGENTE
    def test_agente_ajax(self):

        response = self.client.post(
            '/agente-ajax/',
            {
                'pregunta': 'hola'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST DOCENTE
    def test_docente_ajax(self):

        response = self.client.post(
            '/docente/ajax/',
            {
                'accion': 'perfil'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST EVALUADOR
    def test_evaluador_ajax(self):

        response = self.client.post(
            '/evaluador/ajax/',
            {
                'accion': 'evaluaciones'
            }
        )

        self.assertEqual(response.status_code, 200)

    # ✅ TEST GENERADOR
    def test_generador_ajax(self):

        response = self.client.post(
            '/generador/ajax/',
            {
                'accion': 'generar'
            }
        )

        self.assertEqual(response.status_code, 200)