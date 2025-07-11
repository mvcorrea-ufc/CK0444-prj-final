# analise_dados.py
"""
Script simples para análise de dados educacionais vs políticos
Execute: python analise_dados.py dados.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

def processar_dados(arquivo):
    """Processa dados educacionais e políticos"""
    
    print(f"Carregando dados de: {arquivo}")
    df = pd.read_csv(arquivo)
    print(f"Dados carregados: {len(df)} municípios")
    
    # Mapeamento de partidos por espectro
    party_map = {
        'PT': 'ESQUERDA', 'PCdoB': 'ESQUERDA', 'PSOL': 'ESQUERDA',
        'PDT': 'CENTRO_ESQUERDA', 'PSB': 'CENTRO_ESQUERDA', 'PV': 'CENTRO_ESQUERDA',
        'MDB': 'CENTRO', 'PSDB': 'CENTRO', 'PSD': 'CENTRO', 'PODE': 'CENTRO',
        'DEM': 'CENTRO_DIREITA', 'REPUBLICANOS': 'CENTRO_DIREITA', 'PP': 'CENTRO_DIREITA',
        'PL': 'DIREITA', 'PATRIOTA': 'DIREITA', 'PSL': 'DIREITA', 'NOVO': 'DIREITA'
    }
    
    # Criar features
    df['PARTIDO'] = df['partido'].str.upper()
    df['ESPECTRO_POLITICO'] = df['PARTIDO'].map(party_map).fillna('OUTROS')
    df['REGIAO'] = df['regiao'].map({'N': 'Norte', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'SE': 'Sudeste', 'S': 'Sul'})
    df['INDICE_APROVACAO'] = (df['TX_APROVACAO_5ANO'] + df['TX_APROVACAO_9ANO']) / 2
    
    mediana = df['INDICE_APROVACAO'].median()
    df['ACIMA_MEDIA'] = (df['INDICE_APROVACAO'] > mediana).astype(int)
    
    print("Features criadas com sucesso!")
    return df

def gerar_estatisticas(df):
    """Gera estatísticas básicas"""
    
    print("\n" + "="*50)
    print("ESTATÍSTICAS DESCRITIVAS")
    print("="*50)
    
    print(f"Total de municípios: {len(df)}")
    print(f"Aprovação média 5º ano: {df['TX_APROVACAO_5ANO'].mean():.3f}")
    print(f"Aprovação média 9º ano: {df['TX_APROVACAO_9ANO'].mean():.3f}")
    print(f"Índice geral médio: {df['INDICE_APROVACAO'].mean():.3f}")
    
    print(f"\nDistribuição por região:")
    for regiao, count in df['REGIAO'].value_counts().items():
        pct = count/len(df)*100
        print(f"  {regiao}: {count} ({pct:.1f}%)")
    
    print(f"\nDistribuição por espectro político:")
    for espectro, count in df['ESPECTRO_POLITICO'].value_counts().items():
        pct = count/len(df)*100
        print(f"  {espectro}: {count} ({pct:.1f}%)")
    
    print(f"\nPerformance por espectro político:")
    performance = df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    for espectro in performance.index:
        media = performance.loc[espectro, 'mean']
        count = performance.loc[espectro, 'count']
        print(f"  {espectro}: {media:.3f} ({count} municípios)")

def gerar_graficos(df):
    """Gera gráficos de análise"""
    
    print(f"\nGerando gráficos...")
    Path("graficos").mkdir(exist_ok=True)
    
    # 1. Distribuição das aprovações
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 3, 1)
    plt.hist(df['TX_APROVACAO_5ANO'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('Distribuição - Aprovação 5º Ano')
    plt.xlabel('Taxa de Aprovação')
    plt.ylabel('Frequência')
    plt.axvline(df['TX_APROVACAO_5ANO'].mean(), color='red', linestyle='--', label=f'Média: {df["TX_APROVACAO_5ANO"].mean():.3f}')
    plt.legend()
    
    plt.subplot(2, 3, 2)
    plt.hist(df['TX_APROVACAO_9ANO'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    plt.title('Distribuição - Aprovação 9º Ano')
    plt.xlabel('Taxa de Aprovação')
    plt.ylabel('Frequência')
    plt.axvline(df['TX_APROVACAO_9ANO'].mean(), color='red', linestyle='--', label=f'Média: {df["TX_APROVACAO_9ANO"].mean():.3f}')
    plt.legend()
    
    plt.subplot(2, 3, 3)
    plt.scatter(df['TX_APROVACAO_5ANO'], df['TX_APROVACAO_9ANO'], alpha=0.6, color='purple')
    plt.title('Correlação 5º vs 9º Ano')
    plt.xlabel('Taxa Aprovação 5º Ano')
    plt.ylabel('Taxa Aprovação 9º Ano')
    plt.plot([0.8, 1.0], [0.8, 1.0], 'r--', alpha=0.8)
    
    plt.subplot(2, 3, 4)
    espectro_counts = df['ESPECTRO_POLITICO'].value_counts()
    plt.bar(range(len(espectro_counts)), espectro_counts.values, color='lightcoral')
    plt.title('Distribuição por Espectro Político')
    plt.ylabel('Número de Municípios')
    plt.xticks(range(len(espectro_counts)), espectro_counts.index, rotation=45, ha='right')
    
    plt.subplot(2, 3, 5)
    df.boxplot(column='INDICE_APROVACAO', by='ESPECTRO_POLITICO', ax=plt.gca())
    plt.title('Desempenho por Espectro Político')
    plt.suptitle('')  # Remove título automático do pandas
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Índice de Aprovação')
    
    plt.subplot(2, 3, 6)
    performance_media = df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].mean().sort_values(ascending=False)
    plt.bar(range(len(performance_media)), performance_media.values, color='gold')
    plt.title('Performance Média por Espectro')
    plt.ylabel('Índice de Aprovação Médio')
    plt.xticks(range(len(performance_media)), performance_media.index, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('graficos/analise_completa.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Análise por região
    if 'REGIAO' in df.columns and df['REGIAO'].notna().any():
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        regiao_counts = df['REGIAO'].value_counts()
        plt.pie(regiao_counts.values, labels=regiao_counts.index, autopct='%1.1f%%')
        plt.title('Distribuição por Região')
        
        plt.subplot(2, 2, 2)
        df.boxplot(column='INDICE_APROVACAO', by='REGIAO', ax=plt.gca())
        plt.title('Desempenho por Região')
        plt.suptitle('')
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 3)
        performance_regiao = df.groupby('REGIAO')['INDICE_APROVACAO'].mean().sort_values(ascending=False)
        plt.bar(performance_regiao.index, performance_regiao.values, color='lightsteelblue')
        plt.title('Performance Média por Região')
        plt.ylabel('Índice de Aprovação')
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 4)
        # Heatmap região vs espectro
        pivot_data = df.groupby(['REGIAO', 'ESPECTRO_POLITICO'])['INDICE_APROVACAO'].mean().unstack(fill_value=0)
        if not pivot_data.empty:
            sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd')
            plt.title('Performance: Região vs Espectro')
        
        plt.tight_layout()
        plt.savefig('graficos/analise_regional.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print("Gráficos salvos em: graficos/")

def testar_hipoteses(df):
    """Testa hipóteses estatísticas básicas"""
    
    print(f"\n" + "="*50)
    print("TESTES DE HIPÓTESES")
    print("="*50)
    
    try:
        from scipy import stats
        
        # Teste ANOVA: diferença entre espectros políticos
        grupos = [grupo['INDICE_APROVACAO'].values for nome, grupo in df.groupby('ESPECTRO_POLITICO') if len(grupo) > 1]
        
        if len(grupos) > 1:
            f_stat, p_value = stats.f_oneway(*grupos)
            print(f"ANOVA - Diferença entre espectros políticos:")
            print(f"  F-statistic: {f_stat:.3f}")
            print(f"  P-value: {p_value:.6f}")
            print(f"  Significativo (p < 0.05): {'SIM' if p_value < 0.05 else 'NÃO'}")
        
        # Correlação entre 5º e 9º anos
        corr_coef, p_corr = stats.pearsonr(df['TX_APROVACAO_5ANO'], df['TX_APROVACAO_9ANO'])
        print(f"\nCorrelação entre 5º e 9º anos:")
        print(f"  Coeficiente de Pearson: {corr_coef:.3f}")
        print(f"  P-value: {p_corr:.6f}")
        print(f"  Correlação significativa: {'SIM' if p_corr < 0.05 else 'NÃO'}")
        
    except ImportError:
        print("Scipy não disponível. Pulando testes estatísticos.")
        print("Para instalar: pip install scipy")

def salvar_dataset(df, arquivo_saida):
    """Salva dataset processado"""
    
    df.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"\nDataset processado salvo: {arquivo_saida}")
    print(f"Colunas finais: {len(df.columns)}")
    print(f"Colunas: {list(df.columns)}")

def main():
    """Função principal"""
    
    if len(sys.argv) != 2:
        print("Uso: python analise_dados.py arquivo.csv")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    
    if not Path(arquivo_entrada).exists():
        print(f"Erro: Arquivo {arquivo_entrada} não encontrado")
        sys.exit(1)
    
    try:
        print("ANÁLISE DE DADOS - EDUCAÇÃO vs POLÍTICA")
        print("="*50)
        
        # Processar dados
        df = processar_dados(arquivo_entrada)
        
        # Gerar estatísticas
        gerar_estatisticas(df)
        
        # Gerar gráficos
        gerar_graficos(df)
        
        # Testes estatísticos
        testar_hipoteses(df)
        
        # Salvar dataset
        arquivo_saida = arquivo_entrada.replace('.csv', '_processado.csv')
        salvar_dataset(df, arquivo_saida)
        
        print(f"\n" + "="*50)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("="*50)
        print(f"Arquivos gerados:")
        print(f"  - Dataset processado: {arquivo_saida}")
        print(f"  - Gráficos: graficos/analise_completa.png")
        print(f"  - Análise regional: graficos/analise_regional.png")
        
        # Insights principais
        melhor_espectro = df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].mean().idxmax()
        melhor_performance = df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].mean().max()
        
        print(f"\nINSIGHT PRINCIPAL:")
        print(f"  Espectro político com melhor desempenho: {melhor_espectro} ({melhor_performance:.3f})")
        
        municipios_acima_media = df['ACIMA_MEDIA'].sum()
        print(f"  Municípios acima da média nacional: {municipios_acima_media}/{len(df)}")
        
    except Exception as e:
        print(f"Erro durante análise: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
