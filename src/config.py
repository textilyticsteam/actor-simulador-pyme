from pathlib import Path

MODEL_PATH = Path("modelos/modelo_costos_camisa.joblib")

FEATURES = [
    "Alternativa",
    "segmento",
    "Estrellas",
    "Cantidad_Resenas",
    "precio_por_metro",
    "metro",
    "precio_venta_usd",
    "descuento_pct",
]

COLUMNAS_CATEGORICAS = [
    "Alternativa",
    "segmento",
]

COLUMNAS_NUMERICAS = [
    "Estrellas",
    "Cantidad_Resenas",
    "precio_por_metro",
    "metro",
    "precio_venta_usd",
    "descuento_pct",
]

METROS_POR_CAMISA_DEFAULT = 1.5
COSTO_CONFECCION_ARS_DEFAULT = 8000
TIPO_CAMBIO_USD_DEFAULT = 1500.0
