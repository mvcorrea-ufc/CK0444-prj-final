import pandas as pd
import pickle
import logging
import sys
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, precision_score, recall_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

def load_dataset(dataset_path):
    """Carrega o dataset a partir do caminho fornecido."""
    print(f"Carregando dataset de '{dataset_path}'...")
    return pd.read_csv(dataset_path)

def save_champion_model(model, preprocessor, model_name="champion_model"):
    """Salva o modelo campeão e o pré-processador."""
    model_dir = Path(__file__).parent
    with open(model_dir / f"{model_name}.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(model_dir / "preprocessor.pkl", "wb") as f:
        pickle.dump(preprocessor, f)
    print(f"Modelo '{model_name}.pkl' e 'preprocessor.pkl' salvos em '{model_dir}'.")

def run_experiment(X, y, preprocessor):
    """Executa o benchmark entre os modelos para encontrar o campeão."""
    print("Iniciando benchmark dos modelos...")
    
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, solver='liblinear'),
        'RandomForest': RandomForestClassifier()
    }

    params = {
        'LogisticRegression': {'classifier__C': [0.1, 1, 10]},
        'RandomForest': {'classifier__n_estimators': [50, 100, 200], 'classifier__max_depth': [5, 10, None]}
    }

    results = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for model_name, model in models.items():
        # Cria um pipeline que inclui pré-processamento, SMOTE e o classificador
        pipeline = ImbPipeline(steps=[
            ('preprocessor', preprocessor),
            ('smote', SMOTE(random_state=42)),
            ('classifier', model)
        ])
        
        grid_search = GridSearchCV(pipeline, params[model_name], cv=skf, scoring='roc_auc', n_jobs=-1)
        grid_search.fit(X, y)
        
        results[model_name] = {
            'best_score': grid_search.best_score_,
            'best_params': grid_search.best_params_,
            'best_estimator': grid_search.best_estimator_
        }
        print(f"  - {model_name}: Melhor ROC AUC = {grid_search.best_score_:.4f}")

    # Seleciona o melhor modelo com base no score
    best_model_name = max(results, key=lambda k: results[k]['best_score'])
    print(f"\nMelhor modelo encontrado: {best_model_name} com ROC AUC de {results[best_model_name]['best_score']:.4f}")
    
    return results[best_model_name]['best_estimator']

def main(dataset_path):
    """Função principal para orquestrar o pipeline de treinamento do modelo."""
    
    # Carregar os dados
    df = load_dataset(dataset_path)

    # Engenharia de Features e definição do Alvo
    # Alvo: Classificar se a taxa de aprovação do 9º ano é 'Alta' (acima da mediana) ou 'Baixa'
    median_aprovacao = df['TX_APROVACAO_9ANO'].median()
    df['PERFORMANCE_ALVO'] = (df['TX_APROVACAO_9ANO'] > median_aprovacao).astype(int)
    print(f"Problema de classificação definido: PERFORMANCE_ALVO (1 se TX_APROVACAO_9ANO > {median_aprovacao:.3f}, 0 caso contrário)")

    # Definir features (X) e alvo (y)
    # Usaremos o partido e as taxas do 5º ano para prever a performance no 9º
    features = ['PARTIDO', 'TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO']
    target = 'PERFORMANCE_ALVO'
    
    X = df[features]
    y = df[target]

    # Pré-processamento: One-Hot Encode para a coluna 'PARTIDO'
    # O restante das colunas numéricas não precisa de scaling para os modelos escolhidos
    categorical_features = ['PARTIDO']
    numeric_features = ['TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough' # Mantém as colunas numéricas
    )

    # Executar o experimento para encontrar o melhor modelo
    champion_model = run_experiment(X, y, preprocessor)

    # Salvar o modelo campeão e o pré-processador
    save_champion_model(champion_model, preprocessor)

if __name__ == "__main__":
    # O caminho para o dataset é fixo, pois ele é um artefato do job anterior
    dataset_path = Path(__file__).parent.parent / "sdp-data" / "dados_completos.csv"
    
    if not dataset_path.exists():
        print(f"Erro: Dataset '{dataset_path}' não encontrado.")
        print("Certifique-se de que a pipeline de dados foi executada com sucesso.")
        sys.exit(1)
        
    main(dataset_path)