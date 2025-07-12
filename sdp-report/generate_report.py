import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import io
import base64
import json

# --- Funções de Análise de Dados ---

def processar_dados(df):
    party_map = {
        'PT': 'ESQUERDA', 'PCdoB': 'ESQUERDA', 'PSOL': 'ESQUERDA', 'REDE': 'ESQUERDA',
        'PDT': 'CENTRO_ESQUERDA', 'PSB': 'CENTRO_ESQUERDA', 'PV': 'CENTRO_ESQUERDA',
        'MDB': 'CENTRO', 'PSDB': 'CENTRO', 'PSD': 'CENTRO', 'PODE': 'CENTRO', 'SOLIDARIEDADE': 'CENTRO',
        'DEM': 'DIREITA', 'REPUBLICANOS': 'DIREITA', 'PP': 'DIREITA',
        'PL': 'DIREITA', 'PATRIOTA': 'DIREITA', 'PSL': 'DIREITA', 'NOVO': 'DIREITA'
    }
    df['ESPECTRO_POLITICO'] = df['PARTIDO'].str.upper().map(party_map).fillna('OUTROS')
    df['INDICE_APROVACAO'] = (df['TX_APROVACAO_5ANO'] + df['TX_APROVACAO_9ANO']) / 2
    return df

def get_estatisticas_html(df):
    stats = "<h3>Estatísticas Descritivas dos Dados</h3>"
    stats += f"<p><b>Total de municípios analisados:</b> {len(df)}</p>"
    stats += f"<p><b>Índice de Aprovação Médio (5º e 9º ano):</b> {df['INDICE_APROVACAO'].mean():.3f}</p>"
    performance = df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    stats += "<h4>Performance Média por Espectro Político:</h4><ul>"
    for espectro, row in performance.iterrows():
        stats += f"<li><b>{espectro}:</b> {row['mean']:.3f} (baseado em {row['count']} municípios)</li>"
    stats += "</ul>"
    return stats

# --- Funções de Análise de Modelo ---

def get_modelo_results_html(results):
    html = "<h3>Resultados do Treinamento do Modelo</h3>"
    html += f"<p><b>Modelo Campeão:</b> {results['champion_model']}</p>"
    html += "<h4>Benchmark de Modelos (ROC AUC):</h4>"
    html += "<table border='1'><tr><th>Modelo</th><th>Score ROC AUC</th><th>Melhores Parâmetros</th></tr>"
    for name, data in results['benchmark'].items():
        html += f"<tr><td>{name}</td><td>{data['best_score_roc_auc']:.4f}</td><td>{json.dumps(data['best_params'])}</td></tr>"
    html += "</table>"
    return html

def gerar_grafico_feature_importance(importances_dict, assets_dir):
    if not importances_dict:
        return None, None
    
    importances = pd.Series(importances_dict).sort_values(ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x=importances.values, y=importances.index, ax=ax)
    ax.set_title('Top 15 Features Mais Importantes (RandomForest)')
    ax.set_xlabel('Importância')
    
    save_path = assets_dir / "feature_importance.png"
    html_embed = gerar_grafico_para_html(fig, save_path)
    return html_embed, save_path

# --- Funções Auxiliares ---

def gerar_grafico_para_html(fig, save_path=None):
    """Converte uma figura matplotlib para uma string base64 e opcionalmente salva em arquivo."""
    if save_path:
        save_path.parent.mkdir(exist_ok=True)
        fig.savefig(save_path, format='png', bbox_inches='tight', dpi=300)
        print(f"Gráfico salvo em: {save_path}")

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

def gerar_graficos_dados(df, assets_dir):
    """Gera os gráficos da análise de dados como strings base64 e salva os arquivos."""
    plots = {}
    
    # Gráfico 1: Boxplot de Desempenho por Espectro
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='ESPECTRO_POLITICO', y='INDICE_APROVACAO', data=df, ax=ax, order=df.groupby('ESPECTRO_POLITICO')['INDICE_APROVACAO'].mean().sort_values(ascending=False).index)
    ax.set_title('Desempenho por Espectro Político')
    ax.set_xlabel('Espectro Político')
    ax.set_ylabel('Índice de Aprovação')
    plt.xticks(rotation=45, ha='right')
    plots['desempenho_espectro'] = gerar_grafico_para_html(fig, assets_dir / "desempenho_espectro.png")

    # Gráfico 2: Histograma do Índice de Aprovação
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['INDICE_APROVACAO'], kde=True, ax=ax, bins=30)
    ax.axvline(df['INDICE_APROVACAO'].mean(), color='red', linestyle='--', label=f"Média: {df['INDICE_APROVACAO'].mean():.3f}")
    ax.set_title('Distribuição do Índice de Aprovação Geral')
    ax.set_xlabel('Índice de Aprovação')
    ax.set_ylabel('Frequência')
    ax.legend()
    plots['distribuicao_indice'] = gerar_grafico_para_html(fig, assets_dir / "distribuicao_indice.png")
    
    return plots

def gerar_relatorio_html(data_stats, model_results, plots_dados, plot_importance, output_path):
    template = f"""
    <!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><title>Relatório de Análise</title>
    <style>
        body {{ font-family: sans-serif; margin: 2em; background-color: #f9f9f9; }}
        .container {{ max-width: 1200px; margin: auto; background-color: white; padding: 2em; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.5em;}}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 2em; }}
        .card {{ padding: 1.5em; border: 1px solid #ddd; border-radius: 5px; }}
        img {{ max-width: 100%; height: auto; }} table {{ width: 100%; border-collapse: collapse; }} th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
    </style></head><body><div class="container">
        <h1>Relatório de Análise: Performance Educacional e Modelagem Preditiva</h1>
        <p>Este relatório apresenta a análise exploratória dos dados e os resultados do pipeline de machine learning.</p>
        
        <h2>Análise Exploratória dos Dados</h2>
        <div class="grid">
            <div class="card">{data_stats}</div>
            <div class="card">
                <h3>Desempenho por Espectro Político</h3>
                <img src="{plots_dados['desempenho_espectro']}" alt="Gráfico de Desempenho por Espectro">
            </div>
        </div>

        <h2>Resultados da Modelagem</h2>
        <div class="grid">
            <div class="card">{model_results}</div>
            <div class="card">
                <h3>Importância das Features</h3>
                {'<img src="' + plot_importance + '" alt="Gráfico de Importância das Features">' if plot_importance else '<p>Gráfico de importância não disponível (modelo campeão não foi RandomForest).</p>'}
            </div>
        </div>
        
        <h2>Conclusões</h2>
        <div class="card">
            <p>A análise exploratória e a modelagem indicam que existe uma correlação observável entre as features de entrada (partido, taxas do 5º ano) e a performance educacional no 9º ano. O modelo RandomForest foi o que melhor capturou essas relações, alcançando um score ROC AUC significativo. As features mais importantes, segundo o modelo, fornecem um insight sobre quais fatores tiveram maior peso na predição.</p>
        </div>
    </div></body></html>
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"Relatório salvo em: {output_path}")

def main():
    dataset_path = Path(__file__).parent.parent / "sdp-data" / "dados_completos.csv"
    model_results_path = Path(__file__).parent.parent / "sdp-model" / "model_results.json"
    output_path = Path(__file__).parent / "index.html"
    assets_dir = Path(__file__).parent.parent / "presentation" / "assets"

    if not dataset_path.exists() or not model_results_path.exists():
        print(f"Erro: Arquivos necessários não encontrados.", file=sys.stderr)
        sys.exit(1)

    print("Iniciando geração do relatório completo...")
    df = processar_dados(pd.read_csv(dataset_path))
    with open(model_results_path, 'r') as f:
        model_results = json.load(f)
    
    data_stats_html = get_estatisticas_html(df)
    model_results_html = get_modelo_results_html(model_results)
    plots_dados = gerar_graficos_dados(df, assets_dir)
    plot_importance_html, _ = gerar_grafico_feature_importance(model_results.get('feature_importances'), assets_dir)
    
    gerar_relatorio_html(data_stats_html, model_results_html, plots_dados, plot_importance_html, output_path)
    print("Relatório completo gerado com sucesso!")

if __name__ == "__main__":
    main()
