#!/usr/bin/env python3

import pandas as pd
import requests
import sys
from pathlib import Path

def baixar_dados_eleicoes(url, arquivo_saida):
    """
    Baixa os dados eleitorais se o arquivo não existir localmente.
    """
    arquivo_saida = Path(arquivo_saida)
    if arquivo_saida.exists():
        print(f"Arquivo de eleições '{arquivo_saida}' já existe. Usando o local.")
        return str(arquivo_saida)
    
    print(f"Baixando dados eleitorais de {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Garante que o diretório pai exista
        arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Download dos dados eleitorais concluído em '{arquivo_saida}'.")
        return str(arquivo_saida)
    except requests.exceptions.RequestException as e:
        print(f"Falha no download dos dados eleitorais: {e}", file=sys.stderr)
        raise

def main():
    # Definindo os caminhos
    pasta_base = Path('sdp-data')
    pasta_raw = pasta_base / 'raw_data'
    
    path_educacao = pasta_raw / "dados_educacionais.csv"
    path_eleicoes_raw = pasta_raw / "prefeitos_2020.csv"
    path_final = pasta_base / "dados_completos.csv"
    
    # URL para os dados de prefeitos eleitos em 2020 (fonte: GitHub @marcofaga)
    url_eleicoes = "https://raw.githubusercontent.com/marcofaga/eleicoes2020/master/prefeito2020.csv"

    # Verificar se o arquivo de educação existe
    if not path_educacao.exists():
        print(f"Erro: O arquivo '{path_educacao}' não foi encontrado.", file=sys.stderr)
        print("Por favor, execute 'create_education_data.py' primeiro.", file=sys.stderr)
        sys.exit(1)

    # Carregar dados da educação
    print(f"Lendo dados educacionais de '{path_educacao}'...")
    df_educacao = pd.read_csv(path_educacao)
    
    # Baixar e carregar dados eleitorais
    path_eleicoes_csv = baixar_dados_eleicoes(url_eleicoes, arquivo_saida=path_eleicoes_raw)
    
    print("Processando dados eleitorais...")
    df_eleicoes = pd.read_csv(path_eleicoes_csv, sep=';', encoding='utf-8')
    
    # Filtrar apenas prefeitos eleitos
    df_filtrado = df_eleicoes[(df_eleicoes['cargo'] == 'prefeito') & (df_eleicoes['situacao'] == 'ELEITO')]
    
    # Selecionar colunas e renomear
    df_eleicoes_final = df_filtrado[['codibge', 'partido']].copy()
    df_eleicoes_final.rename(columns={'codibge': 'ID_MUNICIPIO', 'partido': 'PARTIDO'}, inplace=True)
    
    # Garantir que os tipos de dados para a chave de merge sejam os mesmos
    df_educacao['ID_MUNICIPIO'] = df_educacao['ID_MUNICIPIO'].astype(str)
    df_eleicoes_final['ID_MUNICIPIO'] = df_eleicoes_final['ID_MUNICIPIO'].astype(str).str.zfill(7)

    print("Combinando datasets de educação e eleições...")
    df_final = pd.merge(df_educacao, df_eleicoes_final, on='ID_MUNICIPIO', how='inner')

    # Reordenar colunas para melhor visualização
    colunas_ordenadas = [
        'ID_MUNICIPIO', 'PARTIDO',
        'TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO',
        'TX_APROVACAO_9ANO', 'TX_REPROVACAO_9ANO', 'TX_ABANDONO_9ANO'
    ]
    df_final = df_final[colunas_ordenadas]
    
    # Remover linhas onde o merge não encontrou um partido
    df_final.dropna(subset=['PARTIDO'], inplace=True)

    df_final.to_csv(path_final, index=False)
    print(f"Arquivo final combinado '{path_final}' criado com sucesso com {len(df_final)} registros.")

if __name__ == "__main__":
    main()
