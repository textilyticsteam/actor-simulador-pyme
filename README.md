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
