import pickle
import pandas as pd
from pathlib import Path

class PerformancePredictionService:
    """
    Serviço para prever a performance educacional de um município.
    """

    def __init__(self):
        """
        Carrega o modelo e o pré-processador a partir dos arquivos salvos.
        """
        base_dir = Path(__file__).parent.parent.parent.parent / 'sdp-model'
        model_path = base_dir / 'champion_model.pkl'
        preprocessor_path = base_dir / 'preprocessor.pkl'

        print(f"Carregando modelo de: {model_path}")
        print(f"Carregando pré-processador de: {preprocessor_path}")

        with open(model_path, 'rb') as f_model:
            self.model = pickle.load(f_model)
        
        with open(preprocessor_path, 'rb') as f_preprocessor:
            self.preprocessor = pickle.load(f_preprocessor)

    def predict(self, input_data: dict) -> dict:
        """
        Realiza a predição com base nos dados de entrada.

        Args:
            input_data (dict): Um dicionário contendo os valores para as features.
                               Ex: {'PARTIDO': 'PSDB', 'TX_APROVACAO_5ANO': 0.8, ...}

        Returns:
            dict: Um dicionário com a predição e o label correspondente.
        """
        # Cria um DataFrame a partir do dicionário de entrada
        df = pd.DataFrame([input_data])
        
        # Garante a ordem correta das colunas, conforme o treinamento
        features = ['PARTIDO', 'TX_APROVACAO_5ANO', 'TX_REPROVACAO_5ANO', 'TX_ABANDONO_5ANO']
        df = df[features]

        # A predição do pipeline (modelo) já inclui o pré-processamento
        prediction = self.model.predict(df)
        prediction_proba = self.model.predict_proba(df)

        # Mapeia o resultado numérico para um label compreensível
        performance_label = "Alta" if prediction[0] == 1 else "Baixa"
        
        return {
            "prediction": int(prediction[0]),
            "performance_label": performance_label,
            "probability": {
                "baixa": round(prediction_proba[0][0], 4),
                "alta": round(prediction_proba[0][1], 4)
            }
        }
