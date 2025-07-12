import pandas as pd
import pickle
import logging
import sys
import json
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

def save_artifacts(model, preprocessor, results, model_name="champion_model"):
    """Salva o modelo, o pré-processador e os resultados do benchmark."""
    model_dir = Path(__file__).parent
    
    # Salvar modelo e pré-processador
    with open(model_dir / f"{model_name}.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(model_dir / "preprocessor.pkl", "wb") as f:
        pickle.dump(preprocessor, f)
        
    # Salvar resultados do benchmark
    with open(model_dir / "model_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Artefatos salvos em '{model_dir}': '{model_name}.pkl', 'preprocessor.pkl', 'model_results.json'.")

def run_experiment(X, y, preprocessor):
    """Executa o benchmark entre os modelos para encontrar o campeão."""
    print("Iniciando benchmark dos modelos...")
    
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, solver='liblinear', random_state=42),
        'RandomForest': RandomForestClassifier(random_state=42)
    }

    params = {
        'LogisticRegression': {'classifier__C': [0.1, 1, 10]},
        'RandomForest': {'classifier__n_estimators': [50, 100], 'classifier__max_depth': [5, 10]}
    }

    benchmark_results = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for model_name, model in models.items():
        pipeline = ImbPipeline(steps=[
            ('preprocessor', preprocessor),
            ('smote', SMOTE(random_state=42)),
            ('classifier', model)
        ])
        
        grid_search = GridSearchCV(pipeline, params[model_name], cv=skf, scoring='roc_auc', n_jobs=-1)
        grid_search.fit(X, y)
        
        benchmark_results[model_name] = {
            'best_score_roc_auc': grid_search.best_score_,
            'best_params': grid_search.best_params_
        }
        print(f"  - {model_name}: Melhor ROC AUC = {grid_search.best_score_:.4f}")

    best_model_name = max(benchmark_results, key=lambda k: benchmark_results[k]['best_score_roc_auc'])
    print(f"\nMelhor modelo encontrado: {best_model_name}")
    
    # Treinar o modelo campeão final com os melhores parâmetros
    best_params = benchmark_results[best_model_name]['best_params']
    champion_classifier = models[best_model_name].set_params(**{k.replace('classifier__', ''): v for k, v in best_params.items()})

    champion_pipeline = ImbPipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', champion_classifier)
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    champion_pipeline.fit(X_train, y_train)
    
    # Extrair feature importances se for RandomForest
    feature_importances = None
    if best_model_name == 'RandomForest':
        # Obter nomes das features após o one-hot encoding
        ohe_feature_names = champion_pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(X.select_dtypes(include=['object']).columns)
        all_feature_names = list(ohe_feature_names) + list(X.select_dtypes(exclude=['object']).columns)
        
        importances = champion_pipeline.named_steps['classifier'].feature_importances_
        feature_importances = dict(zip(all_feature_names, importances))

    final_results = {
        "champion_model": best_model_name,
        "benchmark": benchmark_results,
        "feature_importances": feature_importances
    }
    
    return champion_pipeline, preprocessor, final_results

def main(dataset_path):
    df = load_dataset(dataset_path)
    median_aprovacao = df['TX_APROVACAO_9ANO'].median()
    df['PERFORMANCE_ALVO'] = (df['TX_APROVACAO_9ANO'] > median_aprovacao).astype(int)
    print(f"Problema de classificação definido: PERFORMANCE_ALVO (1 se TX_APROVACAO_9ANO > {median_aprovacao:.3f}, 0 caso contrário)")

    features = ['PARTIDO', 'TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO']
    target = 'PERFORMANCE_ALVO'
    X = df[features]
    y = df[target]

    preprocessor = ColumnTransformer(
        transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), ['PARTIDO'])],
        remainder='passthrough'
    )

    champion_model, final_preprocessor, results = run_experiment(X, y, preprocessor)
    save_artifacts(champion_model, final_preprocessor, results)

if __name__ == "__main__":
    dataset_path = Path(__file__).parent.parent / "sdp-data" / "dados_completos.csv"
    if not dataset_path.exists():
        print(f"Erro: Dataset '{dataset_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    main(dataset_path)
