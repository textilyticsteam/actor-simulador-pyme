from pathlib import Path
import joblib
from src.config import MODEL_PATH


def cargar_modelo(ruta_modelo: Path = MODEL_PATH):
    """Carga el Pipeline preentrenado desde disco sin reentrenar."""
    if not ruta_modelo.exists():
        raise FileNotFoundError(f"No se encontró el artefacto del modelo en: {ruta_modelo}")
    return joblib.load(ruta_modelo)