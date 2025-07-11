> ## **Universidade Federal do Ceará** | **Departamento de Computação**
>
> - **Curso: Bacharelado em Ciência de Dados** 
> - **Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.1)** 
> - **Professor: Lincoln Souza Rocha | E-mail: lincoln@dc.ufc.br**
---
# **Serviço de Predição de Performance Educacional**

Este módulo expõe o modelo de machine learning treinado como uma API RESTful, permitindo que clientes façam predições em tempo real.

## **Estrutura do Serviço**

- **`src/sdp/app.py`**: O entrypoint da aplicação Flask. Define os endpoints da API (`/predict` e `/health`).
- **`src/sdp/service.py`**: Contém a lógica de negócio. Carrega o modelo e o pré-processador, e realiza as predições.
- **`tests/test_app.py`**: Testes de unidade para a API.

## **Como Executar o Serviço**

### 1. Instalar Dependências
Certifique-se de que todas as dependências no arquivo `requirements.txt` da raiz do projeto estão instaladas.
```bash
# Estando na raiz do projeto
uv pip install -r requirements.txt
```

### 2. Iniciar o Servi��o
Para desenvolvimento, você pode usar o servidor de desenvolvimento do Flask. Para um ambiente mais robusto, use o Gunicorn.

**Opção A: Servidor de Desenvolvimento Flask**
```bash
# A partir da raiz do projeto
python sdp-service/src/sdp/app.py
```
O serviço estará disponível em `http://127.0.0.1:5000`.

**Opção B: Servidor de Produção Gunicorn**
```bash
# A partir da raiz do projeto
gunicorn --bind 0.0.0.0:5000 --chdir sdp-service/src "sdp.app:app"
```

### 3. Testar o Serviço
Para verificar se a API está funcionando corretamente, você pode usar os testes de unidade.
```bash
# A partir da raiz do projeto
python -m unittest discover sdp-service/tests
```

## **Como Usar a API**

Envie uma requisição `POST` para o endpoint `/predict` com um corpo JSON contendo os dados de entrada.

**Exemplo com `curl`:**
```bash
curl -X POST http://127.0.0.1:5000/predict \
-H "Content-Type: application/json" \
-d '{
    "PARTIDO": "PSDB",
    "TX_APROVACAO_5ANO": 0.85,
    "TX_REPROVACAO_5ANO": 0.10,
    "TX_ABANDONO_5ANO": 0.05
}'
```

**Resposta Esperada:**
```json
{
  "performance_label": "Alta",
  "prediction": 1,
  "probability": {
    "alta": 0.6789,
    "baixa": 0.3211
  }
}
```
