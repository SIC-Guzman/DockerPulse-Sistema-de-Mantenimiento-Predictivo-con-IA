import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import pickle

# ==============================
# RUTAS (ajústalas solo si cambias la estructura)
# ==============================
RUTA_CSV_ENTRADA = Path("../../data/DockerPulse/datos_entrenamiento.csv")
RUTA_CSV_SALIDA = Path("../data/datos_procesados.csv")
RUTA_SCALER = Path("../models/scaler_features.pkl")

# ==============================
# CONFIGURACIÓN
# ==============================
# Cada fila ≈ 15s → 4 pasos ≈ 1 minuto
FUTURE_STEPS = 4

# Features seleccionadas (balance entre señal y ruido)
FEATURE_COLS = [
    "Host_CPU", "Host_RAM",
    "oracle-db_CPU",
    "nginx-web_CPU",
    "redis-cache_CPU",
    "postgres-db_CPU",
    "rabbitmq-msg_CPU",
    "python-api_CPU",
    "node-service_CPU",
]

TARGET_COL = "Host_CPU_future"


def main():
    print("🔹 Cargando dataset original...")
    df = pd.read_csv(RUTA_CSV_ENTRADA)

    # ==============================
    # LIMPIEZA Y ORDEN
    # ==============================
    print("🔹 Procesando timestamp...")
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%H:%M:%S")
        df = df.sort_values("Timestamp")

    df.dropna(inplace=True)

    # ==============================
    # VARIABLE FUTURA (PREDICCIÓN)
    # ==============================
    print(f"🔹 Creando variable futura a {FUTURE_STEPS * 15} segundos...")
    df[TARGET_COL] = df["Host_CPU"].shift(-FUTURE_STEPS)
    df.dropna(inplace=True)

    # ==============================
    # ESCALADO DE FEATURES
    # ==============================
    print("🔹 Normalizando features...")
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Dataset final
    df_out = pd.DataFrame(X_scaled, columns=FEATURE_COLS)
    df_out[TARGET_COL] = y.values

    # ==============================
    # GUARDADO
    # ==============================
    RUTA_CSV_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_SCALER.parent.mkdir(parents=True, exist_ok=True)

    df_out.to_csv(RUTA_CSV_SALIDA, index=False)
    print(f"✅ Dataset preprocesado guardado en: {RUTA_CSV_SALIDA}")

    with open(RUTA_SCALER, "wb") as f:
        pickle.dump(
            {
                "scaler": scaler,
                "feature_cols": FEATURE_COLS,
                "future_steps": FUTURE_STEPS,
                "target": TARGET_COL,
            },
            f,
        )

    print(f"✅ Scaler guardado en: {RUTA_SCALER}")
    print("📌 Features usadas:", FEATURE_COLS)
    print("🎯 Target:", TARGET_COL)
    print("🚀 Preprocesamiento finalizado correctamente")


if __name__ == "__main__":
    main()
