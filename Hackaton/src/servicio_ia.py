from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from src.notificador_email import enviar_alerta_html
from src.generador_reporte import generar_pdf_incidente

import json
import pickle
import pandas as pd
import time
import asyncio
import docker


try:
    from tensorflow.keras.models import load_model
except ImportError:
    load_model = None

BASE_DIR = Path(__file__).resolve().parent.parent

RUTA_JSON_VIVO = BASE_DIR / "datos_en_vivo.json"
RUTA_SCALER = BASE_DIR / "models" / "scaler_features.pkl"
RUTA_MODELO_PRED = BASE_DIR / "models" / "modelo_prediccion.h5"
RUTA_MODELO_ANOM = BASE_DIR / "models" / "modelo_anomalia.pkl"

MODELOS_CARGADOS = False
scaler = None
modelo_pred = None
modelo_anom = None
feature_cols = []

print(" Cargando Cerebro de IA...")
try:
    if not RUTA_SCALER.exists() or not RUTA_MODELO_PRED.exists():
        raise FileNotFoundError("Faltan archivos de modelos (.pkl o .h5)")

    with open(RUTA_SCALER, "rb") as f:
        scaler_data = pickle.load(f)
    
    scaler = scaler_data["scaler"]
    feature_cols = scaler_data["feature_cols"]

    if load_model:
        modelo_pred = load_model(RUTA_MODELO_PRED, compile=False)
    
    with open(RUTA_MODELO_ANOM, "rb") as f:
        modelo_anom = pickle.load(f)
        
    MODELOS_CARGADOS = True
    print(" IA Cargada: Sistema listo para predecir.")

except Exception as e:
    print(f" ADVERTENCIA: No se pudo cargar la IA ({e}).")
    print(" El sistema funcionará en MODO EMERGENCIA (Solo reglas de CPU > 90%).")

try:
    docker_client = docker.from_env()
except Exception as e:
    print(" ERROR CRÍTICO: No se detecta Docker. Asegúrate de que Docker Desktop esté corriendo.")
    docker_client = None

app = FastAPI(title="DockerPulse Sentinel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RestartRequest(BaseModel):
    container_name: str

def leer_datos_vivos():
    if not RUTA_JSON_VIVO.exists():
        # Retorna estructura vacía si aun no corre el recolector
        return {"timestamp": 0, "host": {}, "contenedores": []}
    
    try:
        with open(RUTA_JSON_VIVO, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"timestamp": 0, "host": {}, "contenedores": []}

def construir_features(datos):
    if not datos.get("host"):
        return None

    features = {
        "Host_CPU": datos["host"].get("cpu", 0),
        "Host_RAM": datos["host"].get("ram", 0),
    }

    conts = {c["nombre"]: c for c in datos.get("contenedores", [])}

    def g(nombre, tipo):
        return conts.get(nombre, {}).get(tipo, 0.0)

    nombres_esperados = [
        "oracle-db", "nginx-web", "redis-cache", "postgres-db", 
        "rabbitmq-msg", "python-api", "node-service"
    ]
    
    for nombre in nombres_esperados:
        features[f"{nombre}_CPU"] = g(nombre, "cpu")
        features[f"{nombre}_RAM"] = g(nombre, "ram")

    return features

def evaluar_ia(datos):
    """
    Retorna la predicción de la IA. Si no hay modelos, retorna valores seguros.
    """
    resultado_default = {
        "prediccion": {"Host_CPU_future": 0, "nivel_riesgo": "BAJO"},
        "anomalia": {"cluster": 0, "es_anomalo": False}
    }

    if not MODELOS_CARGADOS:
        return resultado_default

    try:
        features = construir_features(datos)
        if not features: 
            return resultado_default

        vector = [features.get(col, 0) for col in feature_cols]
        df = pd.DataFrame([vector], columns=feature_cols)
        X = scaler.transform(df)

        cpu_futura = float(modelo_pred.predict(X, verbose=0)[0][0])
        
        if cpu_futura >= 80: nivel = "ALTO"
        elif cpu_futura >= 50: nivel = "MEDIO"
        else: nivel = "BAJO"

        cluster = int(modelo_anom.predict(X)[0])
        es_anomalo = (cluster == 1)

        return {
            "prediccion": {
                "Host_CPU_future": round(cpu_futura, 2),
                "nivel_riesgo": nivel
            },
            "anomalia": {
                "cluster": cluster,
                "es_anomalo": es_anomalo
            }
        }
    except Exception as e:
        print(f"Error en inferencia IA: {e}")
        return resultado_default


@app.get("/api/status")
def api_status():
    datos = leer_datos_vivos()
    ia = evaluar_ia(datos)
    
    return {
        "timestamp": datos.get("timestamp"),
        "host": datos.get("host"),
        "contenedores": datos.get("contenedores", []),
        "prediccion": ia["prediccion"],
        "anomalia": ia["anomalia"],
        "sistema_activo": True
    }

@app.post("/api/restart")
def api_restart(req: RestartRequest):
    """Endpoint para el Botón Manual del Dashboard"""
    if not docker_client:
        raise HTTPException(500, "Docker no está conectado.")
    
    try:
        print(f" Solicitud manual: Reiniciando {req.container_name}...")
        cont = docker_client.containers.get(req.container_name)
        cont.restart()
        return {"ok": True, "mensaje": f"{req.container_name} reiniciado."}
    except docker.errors.NotFound:
        raise HTTPException(404, "Contenedor no encontrado")
    except Exception as e:
        raise HTTPException(500, str(e))

COOLDOWN = 30  
INTERVALO_CHECK = 3 

ultimo_restart = {}

def obtener_peor_contenedor(datos):
    conts = datos.get("contenedores", [])
    if not conts: return None
    return max(conts, key=lambda c: c.get("cpu", 0))

async def sentinel_loop():
    print(" SENTINEL V2.0 ACTIVO: Vigilando infraestructura...")
    
    while True:
        try:
            if RUTA_JSON_VIVO.exists():
                datos = leer_datos_vivos()
                
                peor_cont = obtener_peor_contenedor(datos)
                
                if peor_cont:
                    nombre = peor_cont["nombre"]
                    cpu_actual = peor_cont.get("cpu", 0)
                    
                    ia = evaluar_ia(datos)
                    riesgo_ia = ia["prediccion"]["nivel_riesgo"]
                    

                    gatillo_emergencia = (cpu_actual > 90.0)
                    
                    gatillo_ia = (riesgo_ia == "ALTO")
                    
                    if gatillo_emergencia or gatillo_ia:
                        ahora = time.time()
                        ultimo_tiempo = ultimo_restart.get(nombre, 0)
                        
                        if (ahora - ultimo_tiempo) > COOLDOWN:
                            razon = "EMERGENCIA CPU > 90%" if gatillo_emergencia else "RIESGO IA PREDICHO"
                            
                            print(f" ALERT: {nombre} está en problemas (CPU: {cpu_actual}%). Razón: {razon}")
                            print(f" ACCIÓN: Reiniciando {nombre} automáticamente...")
                            
                            if docker_client:
                                docker_client.containers.get(nombre).restart()
                                ultimo_restart[nombre] = ahora
                                print(f" {nombre} reiniciado. Sistema estabilizándose.")
                                
                                print(" Notificando a Gerencia y DevOps...")
                                
                                try:
                                    ruta_pdf = generar_pdf_incidente(nombre, cpu_actual, riesgo_ia)
                                    print(f" Reporte generado: {ruta_pdf}")
                                except Exception as e_pdf:
                                    print(f" Error generando PDF: {e_pdf}")

                                try:
                                    enviar_alerta_html(nombre, cpu_actual, razon)
                                    print(" Correo enviado.")
                                except Exception as e_email:
                                    print(f" Error enviando correo: {e_email}")
                            
                            
                        else:
                    
                            pass
                            
        except Exception as e:
            print(f" Error en Sentinel Loop: {e}")
            
        await asyncio.sleep(INTERVALO_CHECK)

@app.on_event("startup")
async def iniciar_sentinel():
    # Inicia el bucle en segundo plano al arrancar la API
    asyncio.create_task(sentinel_loop())
