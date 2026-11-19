import numpy as np
import pandas as pd


def ejecutar_inferencia_y_simulacion(
    modelo,
    df_raw: pd.DataFrame,
    df_features: pd.DataFrame,
    metros_por_camisa: float,
    costo_confeccion_ars: float,
    tipo_cambio_usd: float,
) -> pd.DataFrame:
    """Combina la predicción del modelo ML con las reglas del simulador económico PyME."""
    predicciones_ml = modelo.predict(df_features)

    df_res = df_raw.copy()
    df_res["Alternativa"] = df_features["Alternativa"]
    df_res["Costo_Estimado_ML_ARS"] = np.round(predicciones_ml).astype(int)

    costos_nac = []
    costos_imp = []
    puntos_eq = []
    recomendaciones = []

    for _, row in df_features.iterrows():
        p_metro = row["precio_por_metro"]
        p_usd = row["precio_venta_usd"]

        c_nac = (
            round((p_metro * metros_por_camisa) + costo_confeccion_ars)
            if pd.notna(p_metro)
            else None
        )
        c_imp = round(p_usd * tipo_cambio_usd) if pd.notna(p_usd) else None

        # Punto de equilibrio ($/m) frente al precio importado
        p_eq = (
            round((c_imp - costo_confeccion_ars) / metros_por_camisa, 2)
            if c_imp is not None
            else None
        )

        # Decisión económica según los datos disponibles en la fila
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
            rec = "Datos de precio insuficientes"

        costos_nac.append(c_nac)
        costos_imp.append(c_imp)
        puntos_eq.append(p_eq)
        recomendaciones.append(rec)

    df_res["Costo_Nacional_Simulado_ARS"] = costos_nac
    df_res["Costo_Importacion_Simulado_ARS"] = costos_imp
    df_res["Punto_Equilibrio_Metro_ARS"] = puntos_eq
    df_res["Decision_PyME"] = recomendaciones

    return df_res