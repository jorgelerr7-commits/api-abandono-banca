import os
from contextlib import asynccontextmanager

import joblib
import numpy as np
import pandas as pd
import sklearn.compose._column_transformer as column_transformer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sklearn.impute import SimpleImputer

from preprocesamiento import preparar_datos_crudos
from schemas import ClienteInput, PrediccionOutput

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
artefactos = {}

# Compatibilidad al deserializar artefactos exportados con scikit-learn 1.6.1.
if not hasattr(column_transformer, "_RemainderColsList"):
    class _RemainderColsList(list):
        pass
    column_transformer._RemainderColsList = _RemainderColsList


@asynccontextmanager
async def lifespan(app: FastAPI):
    ruta_prep = os.path.join(ARTIFACTS_DIR, "preprocesador_banca.joblib")
    ruta_modelo = os.path.join(ARTIFACTS_DIR, "modelo_knn.joblib")

    if not os.path.exists(ruta_prep) or not os.path.exists(ruta_modelo):
        raise RuntimeError("No se encuentran los archivos .joblib en 'artifacts/'.")

    print("--> Cargando artefactos en memoria RAM...")
    artefactos["preprocesador"] = joblib.load(ruta_prep)
    artefactos["modelo"] = joblib.load(ruta_modelo)

    preprocesador = artefactos["preprocesador"]
    for nombre, transformador, _ in preprocesador.transformers_:
        if hasattr(transformador, "named_steps"):
            for paso in transformador.named_steps.values():
                if isinstance(paso, SimpleImputer) and not hasattr(paso, "_fill_dtype"):
                    paso._fill_dtype = np.dtype("O") if nombre in {"ord", "nom"} else np.dtype("float64")
    print("✅ Artefactos listos para servir inferencias.")

    yield
    artefactos.clear()


app = FastAPI(
    title="API de Predicción de Abandono de Clientes",
    description="Microservicio bancario basado en KNN y ColumnTransformer.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["Frontend"])
def servir_frontend():
    ruta_html = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(ruta_html):
        return FileResponse(ruta_html)
    return {"mensaje": "API de Banca activa. Visita /docs para Swagger UI."}


@app.post("/predict", response_model=PrediccionOutput, tags=["Inferencia"])
def predecir_abandono(cliente: ClienteInput):
    try:
        datos_dict = cliente.model_dump()
        df_crudo = pd.DataFrame([datos_dict])
        df_saneado = preparar_datos_crudos(df_crudo)

        preprocesador = artefactos["preprocesador"]
        if hasattr(preprocesador, "feature_names_in_"):
            df_saneado = df_saneado.reindex(columns=list(preprocesador.feature_names_in_))

        X_inferencia = preprocesador.transform(df_saneado)

        modelo = artefactos["modelo"]
        prediccion_clase = int(modelo.predict(X_inferencia)[0])
        probabilidades = modelo.predict_proba(X_inferencia)[0]

        clases = list(modelo.classes_)
        indice_abandono = clases.index(1) if 1 in clases else -1
        if indice_abandono < 0:
            raise RuntimeError("El modelo no contiene la clase binaria 1 (abandono).")
        prob_abandono = float(probabilidades[indice_abandono])

        if prob_abandono >= 0.70:
            riesgo = "Alto"
            accion = "Contacto telefonico prioritario por el gestor de cuentas y oferta de fidelizacion."
        elif prob_abandono >= 0.40:
            riesgo = "Medio"
            accion = "Envio de encuesta de satisfaccion y campaña informativa sobre ventajas en comisiones."
        else:
            riesgo = "Bajo"
            accion = "Sin accion requerida. Cliente fidelizado."

        return PrediccionOutput(
            id_cliente=cliente.id_cliente,
            abandono=prediccion_clase,
            probabilidad_abandono=round(prob_abandono, 4),
            nivel_riesgo=riesgo,
            accion_recomendada=accion,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el procesamiento de la inferencia: {exc}",
        )


@app.get("/health", tags=["Sistema"])
def estado_servicio():
    return {"estado": "ok", "modelo_cargado": "modelo" in artefactos}
