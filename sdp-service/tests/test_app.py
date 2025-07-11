import unittest
import json
from sdp.app import app

class TestPerformancePredictionAPI(unittest.TestCase):
    def setUp(self):
        """Configura o cliente de teste para cada teste."""
        self.client = app.test_client()
        # Garante que o app esteja em modo de teste
        app.config['TESTING'] = True

    def test_health_check(self):
        """Testa o endpoint de health check."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'status': 'ok'})

    def test_predict_success(self):
        """Testa o endpoint de predição com dados válidos."""
        # Exemplo de dados de entrada
        input_data = {
            "PARTIDO": "PSDB",
            "TX_APROVACAO_5ANO": 0.85,
            "TX_REPROVACAO_5ANO": 0.10,
            "TX_ABANDONO_5ANO": 0.05
        }
        
        response = self.client.post('/predict', 
                                    data=json.dumps(input_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verifica a estrutura da resposta
        response_data = response.get_json()
        self.assertIn('prediction', response_data)
        self.assertIn('performance_label', response_data)
        self.assertIn('probability', response_data)
        self.assertIn('baixa', response_data['probability'])
        self.assertIn('alta', response_data['probability'])
        
        # Verifica os tipos de dados
        self.assertIsInstance(response_data['prediction'], int)
        self.assertIsInstance(response_data['performance_label'], str)
        self.assertIsInstance(response_data['probability']['baixa'], float)

    def test_predict_missing_data(self):
        """Testa o endpoint de predição com dados de entrada incompletos."""
        input_data = {
            "PARTIDO": "MDB"
            # Faltando as outras chaves
        }
        
        response = self.client.post('/predict',
                                    data=json.dumps(input_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertIn('error', response_data)
        self.assertIn('Dados de entrada incompletos', response_data['error'])

    def test_predict_invalid_content_type(self):
        """Testa se a API rejeita requisições que não são JSON."""
        response = self.client.post('/predict',
                                    data="não é json",
                                    content_type='text/plain')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Requisição deve ser do tipo JSON.')

if __name__ == '__main__':
    unittest.main()
