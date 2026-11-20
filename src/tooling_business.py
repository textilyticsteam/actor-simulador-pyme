import json
import numpy as np
import pandas as pd


def _a_float(valor) -> float:
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return np.nan
    try:
        return float(valor)
    except (TypeError, ValueError):
        return np.nan


def evaluar_escenarios_pyme(
    df_raw: pd.DataFrame,
    df_features: pd.DataFrame,
    predicciones_ml: np.ndarray,
    metros_por_camisa: float,
    costo_confeccion_ars: float,
    tipo_cambio_usd: float,
) -> pd.DataFrame:
    """Combina la predicción ML con el simulador económico y las reglas de decisión PyME."""
    df_res = df_raw.copy()
    if "Alternativa" in df_features.columns:
        df_res["Alternativa"] = df_features["Alternativa"]
    df_res["Costo_Estimado_ML_ARS"] = predicciones_ml

    costos_nac = []
    costos_imp = []
    diferencias = []
    puntos_eq = []
    recomendaciones = []

    for _, row in df_res.iterrows():
        p_metro = _a_float(row.get("precio_por_metro"))
        p_usd = _a_float(row.get("precio_venta_usd"))

        c_nac = (
            round((p_metro * metros_por_camisa) + costo_confeccion_ars)
            if pd.notna(p_metro)
            else None
        )
        c_imp = round(p_usd * tipo_cambio_usd) if pd.notna(p_usd) else None

        dif = (c_nac - c_imp) if (c_nac is not None and c_imp is not None) else None
        p_eq = (
            round((c_imp - costo_confeccion_ars) / metros_por_camisa, 2)
            if c_imp is not None
            else None
        )

        if c_nac is not None and c_imp is not None:
            if c_imp < c_nac:
                rec = "Importación (Shein)"
            elif c_nac < c_imp:
                rec = "Producción Nacional"
            else:
                rec = "Empate técnico"
        elif c_imp is not None:
            rec = f"Importar a ${c_imp:,} ARS (conviene producir local solo si tela < ${p_eq:,.0f}/m)"
        elif c_nac is not None:
            usd_eq = round(c_nac / tipo_cambio_usd, 2)
            rec = f"Producir local a ${c_nac:,} ARS (conviene importar solo si prenda < USD {usd_eq})"
        else:
            rec = "Estimación solo por modelo ML (sin precio unitario de referencia)"

        costos_nac.append(c_nac)
        costos_imp.append(c_imp)
        diferencias.append(dif)
        puntos_eq.append(p_eq)
        recomendaciones.append(rec)

    df_res["Costo_Nacional_Simulado_ARS"] = costos_nac
    df_res["Costo_Importacion_Simulado_ARS"] = costos_imp
    df_res["Diferencia_Nac_vs_Imp_ARS"] = diferencias
    df_res["Punto_Equilibrio_Metro_ARS"] = puntos_eq
    df_res["Decision_PyME"] = recomendaciones

    return df_res


def generar_salidas_negocio(
    df_resultados: pd.DataFrame,
    metros_por_camisa: float,
    costo_confeccion_ars: float,
    tipo_cambio_usd: float,
) -> tuple[list[dict], dict]:
    """Formatea los registros individuales (Inference) y los KPIs agregados del lote (Analytics)."""
    items = json.loads(df_resultados.to_json(orient="records"))

    serie_nac = df_resultados["Costo_Nacional_Simulado_ARS"].dropna()
    serie_imp = df_resultados["Costo_Importacion_Simulado_ARS"].dropna()
    serie_eq = df_resultados["Punto_Equilibrio_Metro_ARS"].dropna()

    resumen_analytics = {
        "total_registros_procesados": len(items),
        "parametros_simulacion": {
            "metros_por_camisa": metros_por_camisa,
            "costo_confeccion_ars": costo_confeccion_ars,
            "tipo_cambio_usd": tipo_cambio_usd,
        },
        "costo_estimado_ml_promedio_ars": round(
            float(df_resultados["Costo_Estimado_ML_ARS"].mean()), 2
        ),
        "costo_estimado_ml_min_ars": int(df_resultados["Costo_Estimado_ML_ARS"].min()),
        "costo_estimado_ml_max_ars": int(df_resultados["Costo_Estimado_ML_ARS"].max()),
        "costo_nacional_promedio_ars": round(float(serie_nac.mean()), 2) if not serie_nac.empty else None,
        "costo_importacion_promedio_ars": round(float(serie_imp.mean()), 2) if not serie_imp.empty else None,
        "punto_equilibrio_metro_promedio_ars": round(float(serie_eq.mean()), 2) if not serie_eq.empty else None,
        "distribucion_alternativas": df_resultados["Alternativa"].value_counts().to_dict(),
        "distribucion_decisiones": df_resultados["Decision_PyME"].value_counts().to_dict(),
    }

    return items, resumen_analytics
