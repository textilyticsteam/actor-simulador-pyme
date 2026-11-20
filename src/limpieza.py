import json
import numpy as np
import pandas as pd
from src.config import COLUMNAS_NUMERICAS, FEATURES


def _normalizar_alternativa(valor: object) -> str:
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return "Producción Nacional"
    texto = str(valor).strip().lower()
    if "shein" in texto or "import" in texto:
        return "Importación (Shein)"
    return "Producción Nacional"


def preparar_lote(registros) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Valida y limpia el lote de entrada. Devuelve (df_original, df_features)."""
    if isinstance(registros, str):
        registros = json.loads(registros)

    if not registros or not isinstance(registros, list):
        raise ValueError("El campo 'registros' debe ser una lista no vacía de objetos.")

    df_raw = pd.DataFrame(registros).copy()

    # Asegura que existan todas las columnas requeridas por el modelo
    for col in FEATURES:
        if col not in df_raw.columns:
            df_raw[col] = np.nan

    df_features = df_raw[FEATURES].copy()
    df_features["Alternativa"] = df_features["Alternativa"].apply(_normalizar_alternativa)

    for col in COLUMNAS_NUMERICAS:
        df_features[col] = pd.to_numeric(df_features[col], errors="coerce")

    return df_raw, df_features
