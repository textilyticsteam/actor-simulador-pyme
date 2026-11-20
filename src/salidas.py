import json
import pandas as pd


def formatear_resultados(df_resultados: pd.DataFrame) -> tuple[list[dict], dict]:
    """Convierte el DataFrame final en registros JSON válidos y genera un resumen del lote."""
    items = json.loads(df_resultados.to_json(orient="records"))

    resumen = {
        "total_registros_procesados": len(items),
        "costo_estimado_ml_promedio_ars": round(
            float(df_resultados["Costo_Estimado_ML_ARS"].mean()), 2
        ),
        "costo_estimado_ml_min_ars": int(df_resultados["Costo_Estimado_ML_ARS"].min()),
        "costo_estimado_ml_max_ars": int(df_resultados["Costo_Estimado_ML_ARS"].max()),
        "distribucion_alternativas": df_resultados["Alternativa"].value_counts().to_dict(),
    }

    return items, resumen
