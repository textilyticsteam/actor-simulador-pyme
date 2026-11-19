# Simulador Económico PyME y Predicción de Costos (Actor Apify - Batch)

Actor de Apify diseñado para evaluar en **lotes (Batch)** la conveniencia económica entre producir camisas de algodón localmente o importarlas (Shein), combinando un modelo de Machine Learning preentrenado (`Ridge Regression`) con reglas de punto de equilibrio para toma de decisiones PyME.

## Arquitectura y Cumplimiento Técnico

El proyecto está estructurado de forma modular separando la orquestación del SDK de la lógica de negocio:

- `.actor/`: Configuración del Actor (`actor.json`) y esquema de validación de entrada (`input_schema.json`).
- `modelos/modelo_costos_camisa.joblib`: Pipeline de `scikit-learn` preentrenado fuera del Actor (sin entrenamiento en tiempo de ejecución).
- `src/main.py`: Punto de entrada exclusivo para el SDK de Apify (`get_input`, `push_data`, `set_value`, `set_status_message`).
- `src/config.py`: Parámetros económicos por defecto (`1.5` m/camisa, `$8.000` confección, tipo de cambio `$1.500 ARS/USD`) y lista de variables.
- `src/limpieza.py`: Normalización de categorías y validación de tipos numéricos del lote recibido.
- `src/modelo.py`: Carga del artefacto `.joblib` desde disco.
- `src/prediccion.py`: Inferencia en bloque (*bulk*) y cálculo de costos simulados y punto de equilibrio (`$/m`).
- `src/salidas.py`: Formateo limpio de registros JSON y generación del `RESUMEN_EJECUTIVO` en el Key-Value Store.

## Formato de Entrada (Input JSON)

El Actor recibe los datos directamente a través del SDK de Apify (por ejemplo, enviados desde un escenario programado en **Make**):

```json
{
  "registros": [
    {
      "producto": "Tela Algodón Peinado Local",
      "Alternativa": "Producción Nacional",
      "Estrellas": 4.8,
      "Cantidad_Resenas": 120,
      "precio_por_metro": 8000,
      "metro": 1.5
    },
    {
      "producto": "Camisa Algodón Importada",
      "Alternativa": "Importación (Shein)",
      "Estrellas": 4.7,
      "Cantidad_Resenas": 350,
      "precio_venta_usd": 12,
      "descuento_pct": 10
    }
  ],
  "metros_por_camisa": 1.5,
  "costo_confeccion_ars": 8000,
  "tipo_cambio_usd": 1500
}
