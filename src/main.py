# from apify import Actor
from src.config import (
    COSTO_CONFECCION_ARS_DEFAULT,
    METROS_POR_CAMISA_DEFAULT,
    TIPO_CAMBIO_USD_DEFAULT,
)
from src.limpieza import alinear_columnas_modelo, preparar_lote
from src.modelo import cargar_modelo
from src.prediccion import ejecutar_inferencia_y_simulacion
from src.salidas import formatear_resultados


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        registros = actor_input.get("registros", [])
        metros = float(actor_input.get("metros_por_camisa", METROS_POR_CAMISA_DEFAULT))
        confeccion = float(actor_input.get("costo_confeccion_ars", COSTO_CONFECCION_ARS_DEFAULT))
        tc = float(actor_input.get("tipo_cambio_usd", TIPO_CAMBIO_USD_DEFAULT))

        await Actor.set_status_message("Validando lote de entrada...")
        df_raw, df_features = preparar_lote(registros)

        await Actor.set_status_message("Cargando modelo preentrenado...")
        modelo = cargar_modelo()
        df_features = alinear_columnas_modelo(df_features, modelo)

        await Actor.set_status_message("Ejecutando predicción y simulación PyME...")
        df_resultados = ejecutar_inferencia_y_simulacion(
            modelo=modelo,
            df_raw=df_raw,
            df_features=df_features,
            metros_por_camisa=metros,
            costo_confeccion_ars=confeccion,
            tipo_cambio_usd=tc,
        )

        items, resumen = formatear_resultados(df_resultados)

        await Actor.push_data(items)
        await Actor.set_value("RESUMEN_EJECUTIVO", resumen)
        await Actor.set_status_message(f"Proceso Batch finalizado: {len(items)} registros evaluados.")
