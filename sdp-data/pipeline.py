#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

def run_script(script_name):
    """Executes a Python script and checks for errors."""
    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        print(f"Erro: O script '{script_path}' não foi encontrado.")
        sys.exit(1)
        
    try:
        print(f"--- Executando {script_name} ---")
        # Usa o mesmo interpretador Python que está executando este script
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Saída de erro padrão:")
            print(result.stderr)
        print(f"--- {script_name} concluído com sucesso ---")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_name}:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

def main():
    """
    Pipeline principal de dados.
    Executa os scripts de criação e merge de dados em sequência.
    """
    print("Iniciando a pipeline de dados...")
    
    # Etapa 1: Criar o dataset educacional
    run_script("create_education_data.py")
    
    # Etapa 2: Fazer o merge com os dados eleitorais
    run_script("merge_data.py")
    
    print("Pipeline de dados concluída com sucesso!")
    print("O arquivo final 'dados_completos.csv' está pronto em 'sdp-data/'.")

if __name__ == "__main__":
    main()