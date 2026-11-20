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

    for col in FEATURES:
        if col not in df_raw.columns:
            df_raw[col] = np.nan

    df_features = df_raw[FEATURES].copy()
    df_features["Alternativa"] = df_features["Alternativa"].apply(_normalizar_alternativa)

    # Normaliza 'segmento' manteniendo NaN si viene vacío para que lo impute el Pipeline
    df_features["segmento"] = df_features["segmento"].apply(
        lambda v: np.nan if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() == "" else str(v).strip()
    )

    for col in COLUMNAS_NUMERICAS:
        df_features[col] = pd.to_numeric(df_features[col], errors="coerce")

    return df_raw, df_features


def alinear_columnas_modelo(df_features: pd.DataFrame, modelo) -> pd.DataFrame:
    """Garantiza que df_features tenga exactamente las columnas esperadas por el Pipeline."""
    columnas_esperadas = getattr(modelo, "feature_names_in_", None)
    if columnas_esperadas is None:
        return df_features

    df_alineado = df_features.copy()
    for col in columnas_esperadas:
        if col not in df_alineado.columns:
            df_alineado[col] = np.nan
    return df_alineado[list(columnas_esperadas)]
