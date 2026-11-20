from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from src.config import MODEL_PATH


def cargar_modelo(ruta_modelo: Path = MODEL_PATH):
    """Carga el Pipeline preentrenado desde disco."""
    if not ruta_modelo.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo del modelo en '{ruta_modelo}'. "
            "Verificá que modelo_costos_camisa.joblib esté dentro de la carpeta modelos/."
        )
    return joblib.load(ruta_modelo)


def predecir_costos(modelo, df_features: pd.DataFrame) -> np.ndarray:
    """Ejecuta inferencia ML sobre el lote y devuelve los costos estimados en ARS."""
    predicciones = modelo.predict(df_features)
    return np.round(predicciones).astype(int)
