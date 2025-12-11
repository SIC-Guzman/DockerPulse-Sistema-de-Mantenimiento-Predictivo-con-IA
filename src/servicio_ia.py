# src/servicio_ia.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import pickle
import pandas as pd
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_JSON_VIVO = BASE_DIR / "DockerPulse" / "datos_en_vivo.json"
RUTA_SCALER = BASE_DIR / "models" / "scaler_features.pkl"
RUTA_MODELO_PRED = BASE_DIR / "models" / "modelo_prediccion.h5"
RUTA_MODELO_ANOM = BASE_DIR / "models" / "modelo_anomalia.pkl"

# === Cargar modelos y scaler al iniciar ===
with open(RUTA_SCALER, "rb") as f:
    scaler_data = pickle.load(f)
scaler = scaler_data["scaler"]
feature_cols = scaler_data["feature_cols"]

modelo_pred = load_model(RUTA_MODELO_PRED)

with open(RUTA_MODELO_ANOM, "rb") as f:
    modelo_anom = pickle.load(f)

app = FastAPI(title="DockerPulse – IA en tiempo real")

# CORS para que el frontend pueda llamar al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo puedes restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def obtener_status():
    """
    Lee datos_en_vivo.json, arma el vector de features,
    predice Host_CPU_future y detecta anomalías.
    """
    if not RUTA_JSON_VIVO.exists():
        return {"error": "Aún no hay datos en vivo. Asegúrate de correr recolector.py"}

    with open(RUTA_JSON_VIVO, "r") as f:
        datos_vivos = json.load(f)

    # Construir diccionario de features
    features = {}

    # Host
    features["Host_CPU"] = datos_vivos["host"]["cpu"]
    features["Host_RAM"] = datos_vivos["host"]["ram"]

    # Índice de contenedores
    conts = {c["nombre"]: c for c in datos_vivos.get("contenedores", [])}

    def get_val(nombre_cont, tipo):
        if nombre_cont in conts:
            return conts[nombre_cont].get(tipo, 0.0)
        return 0.0

    # Debe coincidir con preprocesamiento.py
    features["oracle-db_CPU"]     = get_val("oracle-db", "cpu")
    features["oracle-db_RAM"]     = get_val("oracle-db", "ram")
    features["nginx-web_CPU"]     = get_val("nginx-web", "cpu")
    features["nginx-web_RAM"]     = get_val("nginx-web", "ram")
    features["redis-cache_CPU"]   = get_val("redis-cache", "cpu")
    features["redis-cache_RAM"]   = get_val("redis-cache", "ram")
    features["postgres-db_CPU"]   = get_val("postgres-db", "cpu")
    features["postgres-db_RAM"]   = get_val("postgres-db", "ram")
    features["rabbitmq-msg_CPU"]  = get_val("rabbitmq-msg", "cpu")
    features["rabbitmq-msg_RAM"]  = get_val("rabbitmq-msg", "ram")
    features["python-api_CPU"]    = get_val("python-api", "cpu")
    features["python-api_RAM"]    = get_val("python-api", "ram")
    features["node-service_CPU"]  = get_val("node-service", "cpu")
    features["node-service_RAM"]  = get_val("node-service", "ram")

    df = pd.DataFrame([[features[col] for col in feature_cols]], columns=feature_cols)

    X_scaled = scaler.transform(df)

    # 1) Predicción CPU futura
    y_pred = modelo_pred.predict(X_scaled)[0][0]

    # 2) Cluster/anomalía
    cluster = int(modelo_anom.predict(X_scaled)[0])
    es_anomalo = (cluster == 1)

    nivel_riesgo = "BAJO"
    if y_pred >= 80:
        nivel_riesgo = "ALTO"
    elif y_pred >= 50:
        nivel_riesgo = "MEDIO"

    respuesta = {
        "timestamp": datos_vivos["timestamp"],
        "host": datos_vivos["host"],
        "contenedores": datos_vivos["contenedores"],
        "prediccion": {
            "Host_CPU_future": float(round(y_pred, 2)),
            "nivel_riesgo": nivel_riesgo
        },
        "anomalia": {
            "cluster": cluster,
            "es_anomalo": es_anomalo
        }
    }

    return respuesta
