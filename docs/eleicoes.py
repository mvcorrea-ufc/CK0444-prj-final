import pandas as pd
import requests

def baixar_dados_eleicoes(url_eleicoes):
    """Baixa dados eleitorais do GitHub"""
    response = requests.get(url_eleicoes)
    response.raise_for_status()
    
    # Salvar localmente
    with open("prefeito2020.csv", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    return "prefeito2020.csv"

def carregar_dados_eleicoes(path_csv):
    """Carrega e filtra dados eleitorais"""
    # Ler CSV com separador ';'
    df = pd.read_csv(path_csv, sep=';', encoding='utf-8')
    
    # Filtrar apenas prefeitos eleitos
    df_filtrado = df[
        (df['cargo'] == 'prefeito') & 
        (df['situacao'] == 'ELEITO')
    ]
    
    # Selecionar colunas de interesse e renomear
    df_eleicoes = df_filtrado[['codibge', 'partido', 'regiao', 'uf']].copy()
    
    # Converter codibge para string com 7 dígitos (para match com ID_MUNICIPIO)
    df_eleicoes['codibge'] = df_eleicoes['codibge'].astype(str).str.zfill(7)
    
    # Renomear coluna para facilitar merge
    df_eleicoes = df_eleicoes.rename(columns={'codibge': 'ID_MUNICIPIO'})
    
    return df_eleicoes

def adicionar_dados_eleitorais(df_educacao, url_eleicoes="https://raw.githubusercontent.com/marcofaga/eleicoes2020/refs/heads/master/prefeito2020.csv"):
    """
    Adiciona dados eleitorais ao dataframe de educação
    
    Args:
        df_educacao (pd.DataFrame): DataFrame com dados educacionais
        url_eleicoes (str): URL dos dados eleitorais
    
    Returns:
        pd.DataFrame: DataFrame combinado
    """
    
    # Baixar dados eleitorais
    path_eleicoes = baixar_dados_eleicoes(url_eleicoes)
    
    # Carregar e filtrar dados eleitorais
    df_eleicoes = carregar_dados_eleicoes(path_eleicoes)
    
    # Fazer merge usando ID_MUNICIPIO
    df_combinado = df_educacao.merge(
        df_eleicoes, 
        on='ID_MUNICIPIO', 
        how='left'  # left join para manter todos os municípios do dataset educacional
    )
    
    # Reordenar colunas
    colunas_ordenadas = [
        'ID_MUNICIPIO', 
        'uf', 
        'regiao', 
        'partido',
        'TX_APROVACAO_5ANO', 
        'TX_APROVACAO_9ANO'
    ]
    
    df_combinado = df_combinado[colunas_ordenadas]
    
    return df_combinado

def salvar_dados_combinados(df_combinado, arquivo_saida="dados_educacao_eleicoes_2020_2023.csv"):
    """Salva o dataframe combinado"""
    df_combinado.to_csv(arquivo_saida, index=False)
    print(f"Arquivo combinado criado: {arquivo_saida}")
    
    return arquivo_saida