from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

import json
import pickle
import pandas as pd
import time
import asyncio
import docker

from src.notificador_email import enviar_alerta_html
from src.generador_reporte import generar_pdf_incidente

try:
    from tensorflow.keras.models import load_model
except ImportError:
    load_model = None


# ======================================================
# RUTAS
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent

RUTA_JSON_VIVO = BASE_DIR / "datos_en_vivo.json"
RUTA_SCALER = BASE_DIR / "models" / "scaler_features.pkl"
RUTA_MODELO_PRED = BASE_DIR / "models" / "modelo_prediccion.h5"
RUTA_MODELO_ANOM = BASE_DIR / "models" / "modelo_anomalia.pkl"


# ======================================================
# CARGA DE MODELOS
# ======================================================
MODELOS_CARGADOS = False
scaler = None
modelo_pred = None
modelo_anom = None
feature_cols = []
future_steps = 0

print("🧠 Cargando cerebro de IA...")

try:
    with open(RUTA_SCALER, "rb") as f:
        scaler_data = pickle.load(f)

    scaler = scaler_data["scaler"]
    feature_cols = scaler_data["feature_cols"]
    future_steps = scaler_data.get("future_steps", 4)

    if load_model:
        modelo_pred = load_model(RUTA_MODELO_PRED, compile=False)

    with open(RUTA_MODELO_ANOM, "rb") as f:
        modelo_anom = pickle.load(f)["model"]

    MODELOS_CARGADOS = True
    print("✅ IA cargada correctamente")

except Exception as e:
    print(f"⚠️ IA no disponible ({e}) — modo emergencia activo")


# ======================================================
# DOCKER
# ======================================================
try:
    docker_client = docker.from_env()
except Exception:
    docker_client = None
    print("❌ Docker no disponible")


# ======================================================
# FASTAPI
# ======================================================
app = FastAPI(title="DockerPulse Sentinel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RestartRequest(BaseModel):
    container_name: str


# ======================================================
# UTILIDADES
# ======================================================
def leer_datos_vivos():
    if not RUTA_JSON_VIVO.exists():
        return {"timestamp": 0, "host": {}, "contenedores": []}

    try:
        with open(RUTA_JSON_VIVO, "r") as f:
            return json.load(f)
    except Exception:
        return {"timestamp": 0, "host": {}, "contenedores": []}


def construir_features(datos):
    if not datos.get("host"):
        return None

    features = {
        "Host_CPU": datos["host"].get("cpu", 0),
        "Host_RAM": datos["host"].get("ram", 0),
    }

    conts = {c["nombre"]: c for c in datos.get("contenedores", [])}

    for nombre in [
        "oracle-db", "nginx-web", "redis-cache",
        "postgres-db", "rabbitmq-msg",
        "python-api", "node-service"
    ]:
        features[f"{nombre}_CPU"] = conts.get(nombre, {}).get("cpu", 0)

    return features


def evaluar_ia(datos):
    if not MODELOS_CARGADOS:
        return {
            "prediccion_cpu": 0,
            "riesgo_colapso": False,
            "anomalia": False,
            "tiempo_estimado": "N/A"
        }

    features = construir_features(datos)
    if not features:
        return {
            "prediccion_cpu": 0,
            "riesgo_colapso": False,
            "anomalia": False,
            "tiempo_estimado": "N/A"
        }

    df = pd.DataFrame([[features.get(col, 0) for col in feature_cols]], columns=feature_cols)
    X = scaler.transform(df)

    cpu_futura = float(modelo_pred.predict(X, verbose=0)[0][0])
    riesgo = cpu_futura >= 80

    anomalia = modelo_anom.predict(X)[0] == -1

    return {
        "prediccion_cpu": round(cpu_futura, 2),
        "riesgo_colapso": riesgo,
        "anomalia": anomalia,
        "tiempo_estimado": f"{future_steps * 15} segundos"
    }


# ======================================================
# API
# ======================================================
@app.get("/api/status")
def status():
    datos = leer_datos_vivos()
    ia = evaluar_ia(datos)

    return {
        "timestamp": datos.get("timestamp"),
        "host": datos.get("host"),
        "contenedores": datos.get("contenedores", []),
        "ia": ia,
        "sistema_activo": True
    }


@app.post("/api/restart")
def restart(req: RestartRequest):
    if not docker_client:
        raise HTTPException(500, "Docker no disponible")

    try:
        cont = docker_client.containers.get(req.container_name)
        cont.restart()
        return {"ok": True, "mensaje": f"{req.container_name} reiniciado"}
    except docker.errors.NotFound:
        raise HTTPException(404, "Contenedor no encontrado")
    except Exception as e:
        raise HTTPException(500, str(e))


# ======================================================
# SENTINEL LOOP (SELF-HEALING)
# ======================================================
COOLDOWN = 30
INTERVALO = 3
ultimo_restart = {}


async def sentinel_loop():
    print("🛡️ Sentinel activo — vigilando infraestructura")

    while True:
        try:
            datos = leer_datos_vivos()
            conts = datos.get("contenedores", [])

            if conts:
                peor = max(conts, key=lambda c: c.get("cpu", 0))
                nombre = peor["nombre"]
                cpu = peor.get("cpu", 0)

                ia = evaluar_ia(datos)

                gatillo = cpu > 90 or ia["riesgo_colapso"]

                ahora = time.time()
                if gatillo and (ahora - ultimo_restart.get(nombre, 0)) > COOLDOWN:
                    razon = "CPU crítica" if cpu > 90 else "Riesgo predicho por IA"

                    print(f"🚨 {nombre} en riesgo — {razon}")

                    if docker_client:
                        docker_client.containers.get(nombre).restart()
                        ultimo_restart[nombre] = ahora

                        try:
                            generar_pdf_incidente(nombre, cpu, razon)
                            enviar_alerta_html(nombre, cpu, razon)
                        except Exception as e:
                            print(f"⚠️ Error post-incidente: {e}")

        except Exception as e:
            print(f"❌ Error Sentinel: {e}")

        await asyncio.sleep(INTERVALO)


@app.on_event("startup")
async def iniciar():
    asyncio.create_task(sentinel_loop())
