import unittest
import json
from sdp.app import app

class TestPerformancePredictionAPI(unittest.TestCase):
    def setUp(self):
        """Configura o cliente de teste para cada teste."""
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_health_check(self):
        """Testa o endpoint de health check."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200, msg="Health check deve retornar status 200 OK")
        self.assertEqual(response.get_json(), {'status': 'ok'}, msg="Corpo da resposta do health check deve ser {'status': 'ok'}")

    def test_predict_success(self):
        """Testa o endpoint de predição com dados válidos."""
        input_data = {
            "PARTIDO": "PSDB",
            "TX_APROVACAO_5ANO": 0.85,
            "TX_REPROVACAO_5ANO": 0.10,
            "TX_ABANDONO_5ANO": 0.05
        }
        
        response = self.client.post('/predict', 
                                    data=json.dumps(input_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200, msg="Endpoint de predição deve retornar 200 OK para dados válidos")
        
        response_data = response.get_json()
        self.assertIn('prediction', response_data, msg="A resposta deve conter a chave 'prediction'")
        self.assertIn('performance_label', response_data, msg="A resposta deve conter a chave 'performance_label'")
        self.assertIn('probability', response_data, msg="A resposta deve conter a chave 'probability'")
        self.assertIn('baixa', response_data['probability'], msg="Dicionário de probabilidade deve conter a chave 'baixa'")
        self.assertIn('alta', response_data['probability'], msg="Dicionário de probabilidade deve conter a chave 'alta'")
        
        self.assertIsInstance(response_data['prediction'], int, msg="O valor de 'prediction' deve ser um inteiro")
        self.assertIsInstance(response_data['performance_label'], str, msg="O valor de 'performance_label' deve ser uma string")
        self.assertIsInstance(response_data['probability']['baixa'], float, msg="A probabilidade 'baixa' deve ser um float")

    def test_predict_missing_data(self):
        """Testa o endpoint de predição com dados de entrada incompletos."""
        input_data = {"PARTIDO": "MDB"}
        
        response = self.client.post('/predict',
                                    data=json.dumps(input_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 400, msg="API deve retornar 400 Bad Request para dados faltando")
        response_data = response.get_json()
        self.assertIn('error', response_data, msg="A resposta de erro deve conter a chave 'error'")
        self.assertIn('Dados de entrada incompletos', response_data['error'], msg="A mensagem de erro deve indicar quais dados estão faltando")

    def test_predict_invalid_content_type(self):
        """Testa se a API rejeita requisições que não são JSON."""
        response = self.client.post('/predict',
                                    data="não é json",
                                    content_type='text/plain')
        
        self.assertEqual(response.status_code, 400, msg="API deve retornar 400 Bad Request para Content-Type inválido")
        response_data = response.get_json()
        self.assertIn('error', response_data, msg="A resposta de erro deve conter a chave 'error'")
        self.assertEqual(response_data['error'], 'Requisição deve ser do tipo JSON.', msg="A mensagem de erro deve indicar que a requisição precisa ser JSON")

if __name__ == '__main__':
    unittest.main()
