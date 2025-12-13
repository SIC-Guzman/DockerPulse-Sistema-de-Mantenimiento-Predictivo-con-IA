# src/servicio_ia.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import pickle
import pandas as pd
from tensorflow.keras.models import load_model

# === Rutas base ===
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠ IMPORTANTE:
# El recolector en Linux está escribiendo en:
#   ./datos_en_vivo.json  (raíz del proyecto)
# Así que aquí debemos leer ESE archivo, no DockerPulse/datos_en_vivo.json
RUTA_JSON_VIVO = BASE_DIR / "datos_en_vivo.json"

RUTA_SCALER = BASE_DIR / "models" / "scaler_features.pkl"
RUTA_MODELO_PRED = BASE_DIR / "models" / "modelo_prediccion.h5"
RUTA_MODELO_ANOM = BASE_DIR / "models" / "modelo_anomalia.pkl"

# === Cargar scaler + columnas ===
with open(RUTA_SCALER, "rb") as f:
    scaler_data = pickle.load(f)

scaler = scaler_data["scaler"]
feature_cols = scaler_data["feature_cols"]

# === FIX IMPORTANTE ===
# Se carga el modelo sin compilar para evitar el error de deserialización de métricas
modelo_pred = load_model(RUTA_MODELO_PRED, compile=False)

# === Modelo de anomalías ===
with open(RUTA_MODELO_ANOM, "rb") as f:
    modelo_anom = pickle.load(f)

# === Inicializar API ===
app = FastAPI(title="DockerPulse – IA en tiempo real")

# === Configurar CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego puedes restringir a http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Ruta principal ===
@app.get("/api/status")
def obtener_status():
    """
    Lee datos_en_vivo.json, arma vector de features,
    predice Host_CPU_future y detecta anomalías.
    """

    # Verificar que exista el archivo de datos vivos
    if not RUTA_JSON_VIVO.exists():
        return {"error": "Aún no hay datos en vivo. Ejecuta recolector.py"}

    with open(RUTA_JSON_VIVO, "r") as f:
        datos_vivos = json.load(f)

    # ================================
    # Construcción del vector de features
    # ================================
    features = {}

    # Host
    features["Host_CPU"] = datos_vivos["host"]["cpu"]
    features["Host_RAM"] = datos_vivos["host"]["ram"]

    # Contenedores indexados por nombre
    conts = {c["nombre"]: c for c in datos_vivos.get("contenedores", [])}

    def get_val(nombre_cont, tipo):
        return conts.get(nombre_cont, {}).get(tipo, 0.0)

    # === IMPORTANTE ===
    # Coinciden EXACTAMENTE con preprocesamiento.py
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

    # Convertir a DataFrame en el orden correcto
    df = pd.DataFrame([[features[col] for col in feature_cols]], columns=feature_cols)

    # Normalización con scaler
    X_scaled = scaler.transform(df)

    # ================================
    # 1) Predicción IA supervisada
    # ================================
    y_pred = modelo_pred.predict(X_scaled)[0][0]

    if y_pred >= 80:
        nivel_riesgo = "ALTO"
    elif y_pred >= 50:
        nivel_riesgo = "MEDIO"
    else:
        nivel_riesgo = "BAJO"

    # ================================
    # 2) Detección de anomalías
    # ================================
    cluster = int(modelo_anom.predict(X_scaled)[0])
    es_anomalo = (cluster == 1)

    # ================================
    # Respuesta final
    # ================================
    return {
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
