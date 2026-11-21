from pathlib import Path

MODEL_PATH = Path("modelos/modelo_costos_camisa.joblib")

FEATURES = [
    "Alternativa",
    "segmento",
    "vendedor",
    "Estrellas",
    "Cantidad_Resenas",
    "Cantidad_Vendida",
    "descuento_pct",
    "es_marketplace",
]

COLUMNAS_CATEGORICAS = [
    "Alternativa",
    "segmento",
    "vendedor",
]

COLUMNAS_NUMERICAS = [
    "Estrellas",
    "Cantidad_Resenas",
    "Cantidad_Vendida",
    "descuento_pct",
    "es_marketplace",
]

METROS_POR_CAMISA_DEFAULT = 1.5
COSTO_CONFECCION_ARS_DEFAULT = 8000
TIPO_CAMBIO_USD_DEFAULT = 1500.0
