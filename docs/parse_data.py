#!/usr/bin/env python3

import sys
from tx_rend import processar_dados_inep
from eleicoes import adicionar_dados_eleitorais, salvar_dados_combinados

def main():
    url_dados = "https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2023/tx_rend_municipios_2023.zip"
    arquivo_educacao = "taxa_aprovacao_2023_limpo.csv"
    arquivo_final = "dados_educacao_eleicoes_2020_2023.csv"
    
    try:
        # Processar dados educacionais
        df_educacao = processar_dados_inep(url_zip=url_dados, arquivo_saida=arquivo_educacao)
        
        # Adicionar dados eleitorais
        df_combinado = adicionar_dados_eleitorais(df_educacao)
        
        # Salvar resultado final
        salvar_dados_combinados(df_combinado, arquivo_final)
        
        return 0
    except Exception as e:
        if "Connection" in str(e) or "timeout" in str(e).lower():
            print(f"Erro de conexão: {e}")
            print("Solução: Baixe manualmente o arquivo de:")
            print("https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2023/tx_rend_municipios_2023.zip")
            print("Extraia o arquivo .xlsx e execute: python project_parse.py arquivo.xlsx")
        else:
            print(f"Erro: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            # Processar arquivo local de educação
            df_educacao = processar_dados_inep(arquivo_local=sys.argv[1])
            
            # Adicionar dados eleitorais
            df_combinado = adicionar_dados_eleitorais(df_educacao)
            
            # Salvar resultado
            salvar_dados_combinados(df_combinado)
            
        except Exception as e:
            print(f"Erro: {e}")
    else:
        sys.exit(main())
