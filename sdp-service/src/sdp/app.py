from flask import Flask, request, jsonify
from sdp.service import PerformancePredictionService

app = Flask(__name__)

# Inicializa o serviço (carrega o modelo e o pré-processador na memória)
try:
    service = PerformancePredictionService()
    print("Serviço de predição inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o serviço de predição: {e}")
    service = None

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint para receber os dados e retornar a predição de performance.
    """
    if not service:
        return jsonify({'error': 'Serviço não está disponível.'}), 503

    if not request.is_json:
        return jsonify({'error': 'Requisição deve ser do tipo JSON.'}), 400

    try:
        # Pega os dados do corpo da requisição JSON
        data = request.get_json()
        
        # Validação básica dos dados de entrada
        required_keys = ['PARTIDO', 'TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO']
        if not all(key in data for key in required_keys):
            return jsonify({'error': f'Dados de entrada incompletos. Chaves necessárias: {required_keys}'}), 400

        # Chama o serviço para fazer a predição
        result = service.predict(data)
        
        return jsonify(result)

    except Exception as e:
        print(f"Erro durante a predição: {e}")
        return jsonify({'error': 'Ocorreu um erro interno ao processar a requisição.'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check para verificar se o serviço está no ar.
    """
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Executando com o servidor de desenvolvimento do Flask
    # Para produção, use um servidor WSGI como Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
