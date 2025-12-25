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
import os

# --- IMPORTS DE UTILIDAD ---
try:
    from notificador_email import enviar_alerta_html
    from generador_reporte import generar_pdf_incidente
except ImportError:
    def enviar_alerta_html(*args, **kwargs): print("⚠️ Email simulado")
    def generar_pdf_incidente(*args, **kwargs): print("⚠️ PDF simulado")

try:
    from tensorflow.keras.models import load_model
except ImportError:
    load_model = None

# ======================================================
# RUTAS
# ======================================================
CURRENT_DIR = Path(__file__).resolve().parent 
DIR_MODELS = CURRENT_DIR / "models"
RUTA_SCALER = DIR_MODELS / "scaler_features.pkl"
RUTA_MODELO_PRED = DIR_MODELS / "modelo_prediccion.h5"
RUTA_MODELO_ANOM = DIR_MODELS / "modelo_anomalia.pkl"

POSIBLES_RUTAS_JSON = [
    CURRENT_DIR.parent / "datos_en_vivo.json",
    CURRENT_DIR.parent / "DockerPulse" / "datos_en_vivo.json",
    Path("datos_en_vivo.json")
]

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
    if not RUTA_SCALER.exists():
        raise FileNotFoundError(f"No encuentro {RUTA_SCALER}")

    with open(RUTA_SCALER, "rb") as f:
        scaler_data = pickle.load(f)

    scaler = scaler_data["scaler"]
    feature_cols = scaler_data["feature_cols"]
    future_steps = scaler_data.get("future_steps", 4)

    if load_model and RUTA_MODELO_PRED.exists():
        modelo_pred = load_model(RUTA_MODELO_PRED, compile=False)

    if RUTA_MODELO_ANOM.exists():
        with open(RUTA_MODELO_ANOM, "rb") as f:
            modelo_anom = pickle.load(f)["model"]

    MODELOS_CARGADOS = True
    print("✅ IA cargada correctamente desde src/models")

except Exception as e:
    print(f"⚠️ IA no disponible ({e}) — modo emergencia activo")


# ======================================================
# DOCKER
# ======================================================
try:
    docker_client = docker.from_env()
except Exception:
    docker_client = None
    print("❌ Docker no disponible (¿Permisos?)")


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
    ruta_final = None
    for r in POSIBLES_RUTAS_JSON:
        if r.exists():
            ruta_final = r
            break
    
    if not ruta_final:
        return {"timestamp": 0, "host": {}, "contenedores": []}

    try:
        with open(ruta_final, "r") as f:
            return json.load(f)
    except Exception:
        return {"timestamp": 0, "host": {}, "contenedores": []}


def construir_features(datos):
    if not datos.get("host"): return None

    features = {
        "Host_CPU": datos["host"].get("cpu", 0),
        "Host_RAM": datos["host"].get("ram", 0),
    }
    conts = {c["nombre"]: c for c in datos.get("contenedores", [])}

    for col in feature_cols:
        if col not in ["Host_CPU", "Host_RAM"]:
            nombre_cont = col.replace("_CPU", "")
            features[col] = conts.get(nombre_cont, {}).get("cpu", 0)

    return features


def evaluar_ia(datos):
    if not MODELOS_CARGADOS:
        return {"prediccion_cpu": 0, "riesgo_colapso": False, "anomalia": False, "tiempo_estimado": "N/A"}

    features = construir_features(datos)
    if not features:
        return {"prediccion_cpu": 0, "riesgo_colapso": False, "anomalia": False, "tiempo_estimado": "N/A"}

    try:
        row = [features.get(col, 0) for col in feature_cols]
        df = pd.DataFrame([row], columns=feature_cols)
        X = scaler.transform(df)

        # --- AQUÍ ESTABA EL ERROR: CONVERTIR A TIPOS NATIVOS PYTHON ---
        raw_pred = modelo_pred.predict(X, verbose=0)[0][0]
        cpu_futura = float(raw_pred) # Convertir numpy.float a float
        
        raw_anom = modelo_anom.predict(X)[0]
        # Convertir numpy.bool a bool nativo
        riesgo = bool(cpu_futura >= 80)
        anomalia = bool(raw_anom == -1)
        # -------------------------------------------------------------

        return {
            "prediccion_cpu": round(cpu_futura, 2),
            "riesgo_colapso": riesgo,
            "anomalia": anomalia,
            "tiempo_estimado": f"{future_steps * 15} segundos"
        }
    except Exception as e:
        print(f"Error IA: {e}")
        return {"prediccion_cpu": 0, "riesgo_colapso": False, "anomalia": False}


# ======================================================
# API ENDPOINTS
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
    if not docker_client: raise HTTPException(500, "Docker no disponible")
    try:
        docker_client.containers.get(req.container_name).restart()
        return {"ok": True, "mensaje": f"{req.container_name} reiniciado"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ======================================================
# SENTINEL LOOP (SELF-HEALING)
# ======================================================
COOLDOWN = 45 
ultimo_restart = {}

async def sentinel_loop():
    print("🛡️ Sentinel activo — vigilando infraestructura")
    while True:
        try:
            datos = leer_datos_vivos()
            conts = datos.get("contenedores", [])
            
            if conts and MODELOS_CARGADOS:
                ia = evaluar_ia(datos)
                
                for c in conts:
                    nombre = c["nombre"]
                    cpu = c.get("cpu", 0)
                    
                    gatillo_ia = ia["riesgo_colapso"] and cpu > 50
                    gatillo_hard = cpu > 95
                    
                    if gatillo_ia or gatillo_hard:
                        ahora = time.time()
                        if (ahora - ultimo_restart.get(nombre, 0)) > COOLDOWN:
                            razon = "CRÍTICO (CPU > 95%)" if gatillo_hard else "PREDICCIÓN IA (Colapso inminente)"
                            print(f"🚨 ACCIÓN: Reiniciando {nombre} por {razon}")
                            
                            if docker_client:
                                try:
                                    docker_client.containers.get(nombre).restart()
                                    ultimo_restart[nombre] = ahora
                                    
                                    generar_pdf_incidente(nombre, cpu, razon)
                                    enviar_alerta_html(nombre, cpu, razon)
                                except Exception as e:
                                    print(f"Error reiniciando: {e}")

        except Exception as e:
            print(f"❌ Error loop: {e}")

        await asyncio.sleep(2)

@app.on_event("startup")
async def iniciar():
    asyncio.create_task(sentinel_loop())