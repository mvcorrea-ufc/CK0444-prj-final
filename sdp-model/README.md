> ## **Universidade Federal do Ceará** | **Departamento de Computação**
>
> - **Curso: Bacharelado em Ciência de Dados** 
> - **Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.1)** 
> - **Professor: Lincoln Souza Rocha | E-mail: lincoln@dc.ufc.br**
---
# **Pipeline de Treinamento de Modelo**

Este módulo é responsável por treinar, avaliar e selecionar um modelo de classificação para o problema proposto.

## **Problema de Classificação**

O objetivo é prever se a performance de um município na taxa de aprovação do 9º ano será "Alta" ou "Baixa", com base no partido político do prefeito e nas taxas de rendimento do 5º ano.

- **Alvo (Target):** `PERFORMANCE_ALVO` (1 se a taxa de aprovação do 9º ano for maior que a mediana, 0 caso contrário).
- **Features (Variáveis):** `PARTIDO`, `TX_APROVACAO_5ANO`, `TX_REPROVACAO_5ANO`, `TX_ABANDONO_5ANO`.

## **Instruções para Execução**

A pipeline de modelo é projetada para ser executada após a pipeline de dados.

1.  **Instalar Dependências:**
    Certifique-se de que todas as dependências no arquivo `requirements.txt` da raiz do projeto estão instaladas.
    ```bash
    # Estando na raiz do projeto
    uv pip install -r requirements.txt
    ```

2.  **Executar a Pipeline de Modelo:**
    Execute o script da pipeline. Ele automaticamente encontrará o dataset `dados_completos.csv` gerado pela pipeline de dados.
    ```bash
    python sdp-model/pipeline.py
    ```

## **O que a Pipeline Faz?**

1.  **Carrega os Dados:** Lê o arquivo `sdp-data/dados_completos.csv`.
2.  **Engenharia de Features:** Cria a variável alvo `PERFORMANCE_ALVO`.
3.  **Pré-processamento:** Utiliza um `ColumnTransformer` para aplicar One-Hot Encoding na feature categórica `PARTIDO`.
4.  **Benchmark:** Compara o desempenho de `LogisticRegression` e `RandomForestClassifier` usando `GridSearchCV` e validação cruzada para encontrar o melhor modelo e os melhores hiperparâmetros.
5.  **Balanceamento de Dados:** Utiliza `SMOTE` para lidar com o desbalanceamento de classes durante o treinamento.
6.  **Salva os Artefatos:** Salva o pipeline do modelo campeão (`champion_model.pkl`) e o pré-processador (`preprocessor.pkl`) no diretório `sdp-model/`. Estes arquivos serão utilizados pelo módulo de serviço.
