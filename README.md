# Simulador de Costos PyME: Producción Nacional vs. Importación

Servicio cloud en **Apify Store** que consolida **Analytics** e **Inferencia de Machine Learning** para ayudar a PyMEs textiles argentinas a decidir si les conviene confeccionar camisas de algodón localmente o importarlas, calculando en tiempo real el **punto de equilibrio por metro de tela** y el **costo esperado de mercado**.

---

## Equipo — TEXTILYTICSTEAM

Proyecto desarrollado en el marco del **Capstone Project — Samsung Innovation Campus (SIC) 2026** (Especialización en Inteligencia Artificial y Ciencia de Datos):

* **Uriel Murua** — Arquitectura Cloud (Apify Actor), Automatización Batch (Make) e Integración de Datos.
* **Valentina Sacco** — Análisis Exploratorio de Datos (EDA), Ingeniería de Features y Modelado Predictivo.
* **Florencia Moreno** — Análisis de Negocio, Validación del Modelo y Visualización (Dashboard Ejecutivo).

---

## Arquitectura e Integración Automatizada (Make + Apify)

El Actor funciona exclusivamente como motor de inferencia y simulación económica sin lógica de entrenamiento ni iteración interna:

```text
[Google Sheets] ──► [Make (Schedule + Search Rows + Array Aggregator)]
                                           │
                                           ▼ (POST Batch JSON)
                    [Apify Actor: actor-simulador-pyme]
                      ├── src/preprocessing.py    (Limpieza y alineación de features)
                      ├── src/inference.py        (Inferencia Gradient Boosting .joblib)
                      └── src/tooling_business.py (Simulador PyME + KPIs Analytics)
                                           │
                                           ▼ (GET Dataset / Key-Value Store)
                    [Google Sheets Resultados] ──► [Dashboard Ejecutivo]
```

### Escenario de Automatización en Make
*(Guardar la captura del flujo conectado en el repositorio como `docs/escenario_make.png`)*

![Escenario Make](docs/escenario_make.png)

---

## Operaciones Disponibles (`POST` y `GET`)

El Actor consolida ambos servicios de negocio mediante el parámetro `operacion` en un único endpoint:

* **`all` (por defecto):** Ejecuta **Inference + Analytics** en simultáneo. Guarda la tabla fila por fila en el `Dataset` y los KPIs agregados en `RESUMEN_ANALYTICS`.
* **`inference`:** Devuelve únicamente las predicciones unitarias del modelo ML y la decisión económica por producto.
* **`analytics`:** Devuelve únicamente el resumen estadístico agregado del lote evaluado.

### 1. Ejecutar el servicio (`POST`)
Permite disparar una simulación sincrónica (desde Make, n8n o cualquier cliente HTTP) y obtener los resultados en la misma respuesta:

```bash
curl -X POST "https://api.apify.com/v2/acts/linkable_oven_urt~actor-simulador-pyme/run-sync-get-dataset-items?token=TU_APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operacion": "all",
    "metros_por_camisa": 1.5,
    "costo_confeccion_ars": 8000,
    "tipo_cambio_usd": 1500,
    "registros": [
      {
        "producto": "Tela Poplin Algodón Local",
        "Alternativa": "Producción Nacional",
        "segmento": "poplin",
        "vendedor": "sin especificar",
        "Estrellas": 4.7,
        "Cantidad_Resenas": 100,
        "precio_por_metro": 8000,
        "metro": 1.5
      },
      {
        "producto": "Camisa Algodón Importada",
        "Alternativa": "Importación (Shein)",
        "segmento": "Men Shirts",
        "vendedor": "Manfinity",
        "Estrellas": 4.7,
        "Cantidad_Resenas": 100,
        "precio_venta_usd": 12,
        "descuento_pct": 25
      }
    ]
  }'
```

### 2. Consultar documentación y resultados (`GET`)
* **Metadatos y esquema público del Actor:**
  ```bash
  curl -X GET "https://api.apify.com/v2/acts/linkable_oven_urt~actor-simulador-pyme"
  ```
* **Resumen ejecutivo agregado (`RESUMEN_ANALYTICS` en Key-Value Store):**
  ```bash
  curl -X GET "https://api.apify.com/v2/key-value-stores/STORE_ID/records/RESUMEN_ANALYTICS?token=TU_APIFY_TOKEN"
  ```

---

## Formato de Entrada y Salida

### Parámetros de Entrada (`Input`)
| Campo | Tipo | Obligatorio | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- |
| `operacion` | `string` | No | `"all"` | Modo de ejecución: `"all"`, `"inference"` o `"analytics"`. |
| `registros` | `array` | **Sí** | — | Lista de telas nacionales o prendas importadas a evaluar en lote. |
| `metros_por_camisa` | `number` | No | `1.5` | Metros de tela requeridos para confeccionar una camisa. |
| `costo_confeccion_ars` | `integer` | No | `8000` | Costo fijo de taller y mano de obra local por prenda (`$ ARS`). |
| `tipo_cambio_usd` | `number` | No | `1500` | Tipo de cambio de referencia (`$ ARS/USD`) para importación. |

### Ejemplo de Salida (`Dataset` / `Output`)
```json
[
  {
    "producto": "Tela Algodón Peinado Local",
    "Alternativa": "Producción Nacional",
    "Estrellas": 4.8,
    "Cantidad_Resenas": 120,
    "precio_por_metro": 8000,
    "metro": 1.5,
    "Costo_Estimado_ML_ARS": 21361,
    "Costo_Nacional_Simulado_ARS": 20000,
    "Costo_Importacion_Simulado_ARS": null,
    "Punto_Equilibrio_Metro_ARS": null,
    "Decision_PyME": "Producir local a $20,000 ARS (conviene importar solo si prenda < USD 13.33)"
  },
  {
    "producto": "Camisa Algodón Importada",
    "Alternativa": "Importación (Shein)",
    "Estrellas": 4.7,
    "Cantidad_Resenas": 350,
    "precio_venta_usd": 12,
    "descuento_pct": 10,
    "Costo_Estimado_ML_ARS": 19552,
    "Costo_Nacional_Simulado_ARS": null,
    "Costo_Importacion_Simulado_ARS": 18000,
    "Punto_Equilibrio_Metro_ARS": 6666.67,
    "Decision_PyME": "Importar a $18,000 ARS (conviene producir local solo si tela < $6,667/m)"
  }
]
```

---

## Métricas del Modelo y de Negocio

### Desempeño del Modelo Predictivo (`Gradient Boosting`)
Entrenado con validación cruzada agrupada (`GroupKFold`) y evaluado sobre conjunto de prueba independiente (`GroupShuffleSplit` 80/20) sin filtración de precios unitarios:
* **$R^2$ (Test):** `0,7004` (explica el 70% de la variabilidad del costo por camisa).
* **MAE (Test):** `$5.128 ARS`
* **RMSE (Test):** `$11.182 ARS`

### Métricas de Negocio para la PyME
* **Punto de Equilibrio por Metro (`Punto_Equilibrio_Metro_ARS`):** Indica el precio máximo que la PyME puede pagar por metro de tela nacional antes de que convenga importar (ej.: frente a una prenda importada de `USD 12` a `$1.500 ARS/USD` con confección de `$8.000`, el techo rentable de la tela es **`$6.666,67 ARS/m`**).
* **Diferencial Económico (`Diferencia_Nac_vs_Imp_ARS`):** Cuantifica el ahorro directo en pesos argentinos por prenda para respaldar decisiones de abastecimiento.

---

## Consumo de Recursos y Propuesta Comercial (Apify Store)

### Medición Real de Infraestructura (Benchmark en Apify)
| Métrica Operativa | Valor Medido |
| :--- | :--- |
| **Memoria asignada / Pico real** | `512 MB` (`0,5 GB`) / `119,7 MB` pico (`33,4 MB` promedio) |
| **Tiempo total de ejecución** | `7 segundos` (`~1,2 s` de inferencia Python efectiva) |
| **Consumo de Compute Units (CU)** | `0,00097 CU` por ejecución (`0,5 GB × 7 s / 3600 s`) |
| **Costo real de infraestructura** | **~$0,0003 USD** por ejecución |

### Modelo de Monetización Sugerido
Dado el bajo consumo de cómputo (`< 0,001 CU` por corrida) y el impacto directo en la rentabilidad de compras textiles:
* **Modelo Pay-Per-Event (PPE) en Apify Store:**
  * **Nivel Gratuito / Prueba:** Primeras `20 ejecuciones` sin cargo para validación con datos propios de la PyME.
  * **Precio Comercial:** **`$0,05 USD` por ejecución de lote** (hasta 500 productos por corrida).
  * **Rentabilidad Bruta:** Frente a un costo operativo de `$0,0003 USD` por corrida (más comisiones de plataforma), mantiene un **margen operativo superior al 95%**, resultando accesible para cualquier taller o comercio textil (`~$2,50 USD/mes` en corridas semanales).

---

## Licencia
Distribuido bajo licencia **MIT**. Ver archivo `LICENSE` para más detalles.
