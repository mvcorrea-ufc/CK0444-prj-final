#!/usr/bin/env python3

import pandas as pd
import requests
import zipfile
import os
from pathlib import Path
import sys
import time

import time

def baixar_e_extrair_dados(url_zip, pasta_destino="sdp-data/raw_data"):
    """
    Baixa e extrai dados de um arquivo ZIP, com retentativas em caso de falha.
    Usa o arquivo local se já existir para evitar redownloads.
    """
    pasta_destino = Path(pasta_destino)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # Procurar pelo arquivo .xlsx primeiro
    for root, _, files in os.walk(pasta_destino):
        for arquivo in files:
            if arquivo.endswith('.xlsx'):
                print(f"Arquivo XLSX local encontrado: {os.path.join(root, arquivo)}")
                return os.path.join(root, arquivo)

    # Se não encontrar, faz o download com retentativas
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    session = requests.Session()
    session.headers.update(headers)
    
    max_retries = 3
    retry_delay = 10 # segundos

    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1}/{max_retries} de baixar dados de {url_zip}...")
            response = session.get(url_zip, timeout=60, stream=True)
            response.raise_for_status()
            print("Download concluído.")
            
            zip_path = pasta_destino / "dados.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("Extraindo arquivo ZIP...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)
            
            for root, _, files in os.walk(pasta_destino):
                for arquivo in files:
                    if arquivo.endswith('.xlsx'):
                        return os.path.join(root, arquivo)
            
            raise FileNotFoundError("Arquivo XLSX não foi encontrado no ZIP.")

        except requests.exceptions.RequestException as e:
            print(f"Erro no download na tentativa {attempt + 1}: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"Aguardando {retry_delay} segundos para a próxima tentativa...")
                time.sleep(retry_delay)
                retry_delay *= 2 # Aumenta o tempo de espera (backoff exponencial)
            else:
                print("Número máximo de retentativas atingido. Abortando.", file=sys.stderr)
                raise e
    
    raise FileNotFoundError("Falha ao baixar e extrair o arquivo após múltiplas tentativas.")

def processar_dados_educacionais(path_xlsx, arquivo_saida="dados_educacionais.csv"):
    """
    Lê o arquivo XLSX, aplica a lógica de processamento correta e salva o CSV final.
    """
    print("Lendo e processando o arquivo XLSX...")
    
    # Lê a aba correta, pulando as 9 primeiras linhas de metadados
    df = pd.read_excel(path_xlsx, sheet_name="MUNICIPIOS ", skiprows=9, header=None)

    # Define os nomes das colunas com base na estrutura do arquivo
    # As colunas de rendimento (Aprovação, Reprovação, Abandono) se repetem
    colunas = [
        "NU_ANO_CENSO", "NO_REGIAO", "SG_UF", "CO_MUNICIPIO", "NO_MUNICIPIO",
        "NO_CATEGORIA", "NO_DEPENDENCIA",
        # Aprovação
        "APR_FUN_TOTAL", "APR_FUN_AI", "APR_FUN_AF", "APR_1ANO", "APR_2ANO", "APR_3ANO", "APR_4ANO", "APR_5ANO", "APR_6ANO", "APR_7ANO", "APR_8ANO", "APR_9ANO",
        "APR_MED_TOTAL", "APR_MED_1S", "APR_MED_2S", "APR_MED_3S", "APR_MED_4S", "APR_MED_NS",
        # Reprovação
        "REP_FUN_TOTAL", "REP_FUN_AI", "REP_FUN_AF", "REP_1ANO", "REP_2ANO", "REP_3ANO", "REP_4ANO", "REP_5ANO", "REP_6ANO", "REP_7ANO", "REP_8ANO", "REP_9ANO",
        "REP_MED_TOTAL", "REP_MED_1S", "REP_MED_2S", "REP_MED_3S", "REP_MED_4S", "REP_MED_NS",
        # Abandono
        "ABA_FUN_TOTAL", "ABA_FUN_AI", "ABA_FUN_AF", "ABA_1ANO", "ABA_2ANO", "ABA_3ANO", "ABA_4ANO", "ABA_5ANO", "ABA_6ANO", "ABA_7ANO", "ABA_8ANO", "ABA_9ANO",
        "ABA_MED_TOTAL", "ABA_MED_1S", "ABA_MED_2S", "ABA_MED_3S", "ABA_MED_4S", "ABA_MED_NS",
    ]
    
    df = df.iloc[:, :len(colunas)]
    df.columns = colunas

    print("Filtrando dados: Categoria 'Total' e Dependência 'Municipal'...")
    # A lógica correta é filtrar por 'Total' e 'Municipal' (ensino basico é de respnsabilidade do municipio)
    df_filtrado = df[
        (df["NO_CATEGORIA"] == "Total") &
        (df["NO_DEPENDENCIA"] == "Municipal")
    ].copy()

    colunas_interesse = {
        'ID_MUNICIPIO': 'CO_MUNICIPIO',
        'TX_APROVACAO_5ANO': 'APR_5ANO',
        'TX_REPROVACAO_5ANO': 'REP_5ANO',
        'TX_ABANDONO_5ANO': 'ABA_5ANO',
        'TX_APROVACAO_9ANO': 'APR_9ANO',
        'TX_REPROVACAO_9ANO': 'REP_9ANO',
        'TX_ABANDONO_9ANO': 'ABA_9ANO'
    }
    
    df_resultado = df_filtrado[list(colunas_interesse.values())].copy()
    df_resultado.rename(columns={v: k for k, v in colunas_interesse.items()}, inplace=True)

    print("Limpando e normalizando dados...")
    df_resultado['ID_MUNICIPIO'] = df_resultado['ID_MUNICIPIO'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(7)

    for col in df_resultado.columns:
        if col != 'ID_MUNICIPIO':
            # Converte para numérico, tratando '--' como nulo, e divide por 100
            df_resultado[col] = pd.to_numeric(df_resultado[col], errors='coerce') / 100
            df_resultado[col] = df_resultado[col].round(3)

    df_resultado.dropna(inplace=True)
    
    df_resultado.to_csv(arquivo_saida, index=False)
    print(f"Arquivo final '{arquivo_saida}' criado com sucesso com {len(df_resultado)} registros.")
    return arquivo_saida

def main():
    url_dados_inep = "https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2023/tx_rend_municipios_2023.zip"
    
    pasta_base = Path('sdp-data')
    pasta_raw = pasta_base / 'raw_data'
    
    arquivo_final_csv = pasta_raw / "dados_educacionais.csv"

    try:
        path_xlsx = baixar_e_extrair_dados(url_dados_inep, pasta_destino=str(pasta_raw))
        processar_dados_educacionais(path_xlsx, arquivo_saida=str(arquivo_final_csv))

    except Exception as e:
        print(f"Ocorreu um erro no pipeline: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
