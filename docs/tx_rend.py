import pandas as pd
import requests
import zipfile
import os
import time
from pathlib import Path

def baixar_e_extrair_dados(url_zip, pasta_destino="dados_inep"):
    Path(pasta_destino).mkdir(exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    for tentativa in range(3):
        try:
            response = session.get(url_zip, timeout=30, stream=True)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            if tentativa == 2:
                raise e
            time.sleep(2)
            continue
    
    zip_path = f"{pasta_destino}/dados.zip"
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(pasta_destino)
    
    # Buscar arquivo XLSX recursivamente
    for root, dirs, files in os.walk(pasta_destino):
        for arquivo in files:
            if arquivo.endswith('.xlsx'):
                return os.path.join(root, arquivo)
    
    raise FileNotFoundError("Arquivo XLSX não encontrado")

def converter_xlsx_para_csv(path_xlsx):
    """Converte XLSX para CSV"""
    df = pd.read_excel(path_xlsx)
    
    # Converter CO_MUNICIPIO para string antes de salvar CSV
    if 'CO_MUNICIPIO' in df.columns:
        df['CO_MUNICIPIO'] = df['CO_MUNICIPIO'].astype(str).str.zfill(7)
    
    csv_path = path_xlsx.replace('.xlsx', '.csv')
    df.to_csv(csv_path, index=False)
    return csv_path

def carregar_taxa_aprovacao_csv(path_csv):
    # Ler CSV especificando dtype=str para evitar conversão automática
    df = pd.read_csv(path_csv, sep=',', skiprows=9, encoding='utf-8', header=None, low_memory=False, dtype=str)
    
    base_colunas = [
        "NU_ANO_CENSO", "NO_REGIAO", "SG_UF", "CO_MUNICIPIO", "NO_MUNICIPIO",
        "NO_CATEGORIA", "NO_DEPENDENCIA",
        "1_CAT_FUN", "1_CAT_FUN_AI", "1_CAT_FUN_AF",
        "1_CAT_FUN_01", "1_CAT_FUN_02", "1_CAT_FUN_03", "1_CAT_FUN_04",
        "1_CAT_FUN_05", "1_CAT_FUN_06", "1_CAT_FUN_07", "1_CAT_FUN_08", "1_CAT_FUN_09",
        "1_CAT_MED", "1_CAT_MED_01", "1_CAT_MED_02", "1_CAT_MED_03", "1_CAT_MED_04", "1_CAT_MED_NS"
    ]
    
    num_colunas = df.shape[1]
    if len(base_colunas) < num_colunas:
        extras = [f"X{i}" for i in range(num_colunas - len(base_colunas))]
        df.columns = base_colunas + extras
    else:
        df.columns = base_colunas[:num_colunas]
    
    # Filtrar por categoria e dependência "Total"
    df_filtrado = df[
        (df["NO_CATEGORIA"] == "Total") &
        (df["NO_DEPENDENCIA"] == "Total")
    ]
    
    # Selecionar colunas de interesse
    df_resultado = df_filtrado[["CO_MUNICIPIO", "1_CAT_FUN_05", "1_CAT_FUN_09"]].copy()
    df_resultado.columns = ['ID_MUNICIPIO', 'TX_APROVACAO_5ANO', 'TX_APROVACAO_9ANO']
    
    # ID já é string, remover .0 se existir e garantir 7 dígitos
    df_resultado['ID_MUNICIPIO'] = df_resultado['ID_MUNICIPIO'].str.replace('.0', '').str.zfill(7)
    
    # Substituir '--' por NaN
    df_resultado = df_resultado.replace('--', pd.NA)
    
    # Converter taxas para float (já que dtype=str leu tudo como string)
    df_resultado['TX_APROVACAO_5ANO'] = pd.to_numeric(df_resultado['TX_APROVACAO_5ANO'], errors='coerce') / 100
    df_resultado['TX_APROVACAO_9ANO'] = pd.to_numeric(df_resultado['TX_APROVACAO_9ANO'], errors='coerce') / 100
    
    # Arredondar para 3 casas decimais
    df_resultado['TX_APROVACAO_5ANO'] = df_resultado['TX_APROVACAO_5ANO'].round(3)
    df_resultado['TX_APROVACAO_9ANO'] = df_resultado['TX_APROVACAO_9ANO'].round(3)
    
    # Remover linhas com valores NaN
    df_resultado = df_resultado.dropna()
    
    return df_resultado

def processar_dados_inep(url_zip=None, arquivo_local=None, arquivo_saida="taxa_aprovacao_2023_limpo.csv"):
    if arquivo_local and os.path.exists(arquivo_local):
        path_xlsx = arquivo_local
    elif url_zip:
        path_xlsx = baixar_e_extrair_dados(url_zip)
    else:
        raise ValueError("Forneça url_zip ou arquivo_local")
    
    # Converter XLSX para CSV primeiro
    path_csv = converter_xlsx_para_csv(path_xlsx)
    
    # Processar CSV
    df_resultado = carregar_taxa_aprovacao_csv(path_csv)
    df_resultado.to_csv(arquivo_saida, index=False)
    
    print(f"Arquivo criado: {arquivo_saida}")
    
    return df_resultado