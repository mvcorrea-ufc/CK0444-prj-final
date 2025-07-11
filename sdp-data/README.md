> ## **Universidade Federal do Ceará** | **Departamento de Computação**
>
> - **Curso: Bacharelado em Ciência de Dados** 
> - **Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.1)** 
> - **Professor: Lincoln Souza Rocha | E-mail: lincoln@dc.ufc.br**
---
# **Pipeline de Dados do Projeto**

Este módulo é responsável por baixar, limpar, processar e combinar os dados educacionais e eleitorais para o projeto.

## **Instruções para Execução**

1.  **Configurar o Ambiente Virtual:**
    Certifique-se de ter o `uv` instalado. Na raiz do projeto, crie o ambiente virtual:
    ```bash
    uv venv
    ```

2.  **Instalar as Dependências:**
    Instale as bibliotecas necessárias a partir do arquivo `requirements.txt`:
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Executar a Pipeline de Dados:**
    Execute o script principal da pipeline para gerar o dataset completo. O script irá orquestrar a execução dos outros scripts na ordem correta.
    ```bash
    python sdp-data/pipeline.py
    ```

## **O que a Pipeline Faz?**

1.  **`create_education_data.py`:** Baixa os dados de rendimento escolar do INEP, processa e salva o arquivo `sdp-data/dados_educacionais.csv`.
2.  **`merge_data.py`:** Baixa os dados eleitorais de 2020, combina com o arquivo educacional e salva o dataset final em `sdp-data/dados_completos.csv`.

O arquivo `pymetrix.py` não é utilizado neste projeto.
