import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from pathlib import Path
import pickle

# RUTAS
BASE_DIR = Path(__file__).resolve().parent
DIR_MODELS = BASE_DIR / "models"
DIR_MODELS.mkdir(exist_ok=True)

print("♻️ RESTAURANDO MODELOS BORRADOS POR GIT RESET...")

# 1. DATOS FALSOS
df = pd.DataFrame({
    "Host_CPU": np.random.uniform(10, 60, 1000),
    "Host_RAM": np.random.uniform(20, 70, 1000)
})
cols_contenedores = ["oracle-db", "nginx-web", "redis-cache", "postgres-db", "rabbitmq-msg", "python-api", "node-service"]
for c in cols_contenedores:
    df[f"{c}_CPU"] = df["Host_CPU"] * 0.8 + np.random.normal(0, 5, 1000)

features = ["Host_CPU", "Host_RAM"] + [f"{c}_CPU" for c in cols_contenedores]
scaler = MinMaxScaler()
scaler.fit(df[features])

# 2. GUARDAR SCALER
with open(DIR_MODELS / "scaler_features.pkl", "wb") as f:
    pickle.dump({"scaler": scaler, "feature_cols": features, "future_steps": 4}, f)

# 3. GUARDAR MODELO PREDICCION (Simulado para velocidad)
model = Sequential([Dense(10, input_shape=(len(features),)), Dense(1)])
model.compile(loss='mse')
model.fit(scaler.transform(df[features]), df["Host_CPU"], epochs=1, verbose=0)
model.save(DIR_MODELS / "modelo_prediccion.h5")

# 4. GUARDAR DETECTOR ANOMALIAS
iso = IsolationForest().fit(scaler.transform(df[features]))
with open(DIR_MODELS / "modelo_anomalia.pkl", "wb") as f:
    pickle.dump({"model": iso}, f)

print("✅ ¡MODELOS RESTAURADOS! Ahora reinicia el uvicorn.")