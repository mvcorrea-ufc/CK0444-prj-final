# Projeto de Engenharia de Sistemas Inteligentes (CK0444 - 2025.1)

Este projeto implementa um pipeline de MLOps de ponta a ponta, desde a coleta de dados até o deploy de um modelo de machine learning como um serviço de API.

**Objetivo:** Analisar a possível correlação entre o partido político do prefeito de um município e o desempenho educacional (taxas de aprovação, reprovação e abandono) de suas escolas.

---

## Arquitetura e Visão Geral

O projeto é construído sobre uma arquitetura modular e automatizada, garantindo que cada parte do processo seja reprodutível e testável.

```
+-------------------------+      +--------------------------+      +-----------------------+
|                         |      |                          |      |                       |
|      sdp-data           |----->|       sdp-model          |----->|      sdp-service      |
| (Pipeline de Dados)     |      | (Pipeline de Modelo)     |      | (API de Predição)     |
|                         |      |                          |      |                       |
+-------------------------+      +--------------------------+      +-----------------------+
           |                              |                               |
           v                              v                               v
+---------------------------------------------------------------------------------------+
|                                                                                       |
|                                GitHub Actions (CI/CD)                                 |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

1.  **`sdp-data`**: Coleta dados brutos de fontes externas (INEP, TSE), limpa-os e os combina em um dataset unificado (`dados_completos.csv`). Este dataset é o produto final deste módulo.
2.  **`sdp-model`**: Utiliza o dataset gerado para treinar e avaliar múltiplos modelos de classificação. Ele seleciona um "modelo campeão" e o salva junto com um pré-processador de features.
3.  **`sdp-service`**: Carrega o modelo e o pré-processador salvos e os expõe através de uma API RESTful, pronta para receber requisições e retornar predições em tempo real.
4.  **GitHub Actions**: Automatiza todo o fluxo. Cada `push` ou `pull request` aciona um workflow que executa as três etapas em sequência, garantindo a integridade e a funcionalidade do projeto.

---

## Como Usar o Projeto

### Pré-requisitos
- Python 3.10+
- `uv` (ferramenta de gerenciamento de pacotes Python)

### 1. Configuração do Ambiente
Clone o repositório e navegue até a raiz do projeto.

**Crie o ambiente virtual:**
```bash
uv venv
```

**Instale todas as dependências do projeto:**
```bash
uv pip install -r requirements.txt
```

### 2. Execução Local dos Pipelines
Para executar cada etapa manualmente e inspecionar os resultados.

**a) Execute a pipeline de dados:**
```bash
# Ative o ambiente virtual se não estiver usando 'uv run'
source .venv/bin/activate 

# Este comando irá gerar o arquivo sdp-data/dados_completos.csv
python sdp-data/pipeline.py
```

**b) Execute a pipeline de modelo:**
```bash
# Este comando irá gerar os arquivos .pkl em sdp-model/
python sdp-model/pipeline.py
```

**c) Inicie o serviço da API:**
```bash
# Use Gunicorn para um servidor mais robusto
gunicorn --bind 0.0.0.0:5000 --chdir sdp-service/src "sdp.app:app"
```
O serviço estará rodando em `http://127.0.0.1:5000`.

### 3. Interagindo com a API
Com o serviço rodando, você pode enviar requisições para o endpoint `/predict`.

**Exemplo de requisição com `curl`:**
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

**Resposta esperada:**
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
Você também pode usar o notebook `sdp-service/service_cliente.ipynb` para interagir com a API de forma mais interativa.

### 4. Executando os Testes
Para garantir que o serviço da API está funcionando corretamente:
```bash
# Execute os testes a partir da raiz do projeto
uv run --env PYTHONPATH=sdp-service/src python -m unittest discover sdp-service/tests
```

---

## Pipeline de CI/CD com GitHub Actions

O arquivo `.github/workflows/ci-pipeline.yml` define a automação do projeto.

- **Gatilhos:** O workflow é acionado em `push` ou `pull_request` para a branch `main`.
- **Jobs Sequenciais:**
    1.  **`build-data-pipeline`**: Executa a pipeline de dados. Se for bem-sucedido, faz o upload do `dados_completos.csv` como um artefato chamado `sdp-dataset`.
    2.  **`build-model-pipeline`**: Baixa o `sdp-dataset`, executa a pipeline de modelo e faz o upload do `champion_model.pkl` e `preprocessor.pkl` como um artefato chamado `sdp-model`.
    3.  **`test-service-pipeline`**: Baixa o `sdp-model` e executa os testes de unidade do serviço para garantir que a API funciona com os artefatos gerados.

Este fluxo garante que qualquer alteração no código seja automaticamente construída e testada, mantendo a alta qualidade e a confiabilidade do projeto.