from apify import Actor
from src.config import (
    COSTO_CONFECCION_ARS_DEFAULT,
    METROS_POR_CAMISA_DEFAULT,
    TIPO_CAMBIO_USD_DEFAULT,
)
from src.inference import cargar_modelo, predecir_costos
from src.preprocessing import alinear_columnas_modelo, preparar_lote
from src.tooling_business import evaluar_escenarios_pyme, generar_salidas_negocio


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        operacion = str(actor_input.get("operacion", "all")).strip().lower()
        if operacion not in {"all", "inference", "analytics"}:
            operacion = "all"

        registros = actor_input.get("registros", [])
        metros = float(actor_input.get("metros_por_camisa", METROS_POR_CAMISA_DEFAULT))
        confeccion = float(actor_input.get("costo_confeccion_ars", COSTO_CONFECCION_ARS_DEFAULT))
        tc = float(actor_input.get("tipo_cambio_usd", TIPO_CAMBIO_USD_DEFAULT))

        await Actor.set_status_message("Ejecutando preprocesamiento del lote...")
        df_raw, df_features = preparar_lote(registros)

        await Actor.set_status_message("Cargando modelo y ejecutando inferencia...")
        modelo = cargar_modelo()
        df_features = alinear_columnas_modelo(df_features, modelo)
        predicciones_ml = predecir_costos(modelo, df_features)

        await Actor.set_status_message("Calculando métricas de negocio y simulación PyME...")
        df_resultados = evaluar_escenarios_pyme(
            df_raw=df_raw,
            df_features=df_features,
            predicciones_ml=predicciones_ml,
            metros_por_camisa=metros,
            costo_confeccion_ars=confeccion,
            tipo_cambio_usd=tc,
        )

        items, resumen_analytics = generar_salidas_negocio(
            df_resultados=df_resultados,
            metros_por_camisa=metros,
            costo_confeccion_ars=confeccion,
            tipo_cambio_usd=tc,
        )

        if operacion == "analytics":
            await Actor.push_data([resumen_analytics])
            await Actor.set_value("RESUMEN_ANALYTICS", resumen_analytics)
        elif operacion == "inference":
            await Actor.push_data(items)
        else:
            await Actor.push_data(items)
            await Actor.set_value("RESUMEN_ANALYTICS", resumen_analytics)

        await Actor.set_status_message(
            f"Operación '{operacion}' finalizada ({len(items)} registros evaluados)."
        )
