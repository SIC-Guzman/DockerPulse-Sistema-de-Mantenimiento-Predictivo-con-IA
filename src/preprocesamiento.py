import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import pickle

# Ajusta esta ruta si moviste el CSV a otra carpeta
RUTA_CSV_ENTRADA = Path("DockerPulse/datos_entrenamiento.csv")
RUTA_CSV_SALIDA = Path("DockerPulse/datos_procesados.csv")
RUTA_SCALER = Path("models/scaler_features.pkl")

def main():
    # Leer CSV original
    df = pd.read_csv(RUTA_CSV_ENTRADA)

    # Crear columna objetivo: Host_CPU del siguiente instante
    df["Host_CPU_future"] = df["Host_CPU"].shift(-1)

    # Eliminar la última fila (tiene Host_CPU_future = NaN)
    df = df.dropna(subset=["Host_CPU_future"])

    # Columnas numéricas que usaremos como features
    feature_cols = [
        "Host_CPU", "Host_RAM",
        "oracle-db_CPU", "oracle-db_RAM",
        "nginx-web_CPU", "nginx-web_RAM",
        "redis-cache_CPU", "redis-cache_RAM",
        "postgres-db_CPU", "postgres-db_RAM",
        "rabbitmq-msg_CPU", "rabbitmq-msg_RAM",
        "python-api_CPU", "python-api_RAM",
        "node-service_CPU", "node-service_RAM",
    ]

    X = df[feature_cols]
    y = df["Host_CPU_future"]

    # Normalizamos solo las features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Volvemos a DataFrame
    df_out = pd.DataFrame(X_scaled, columns=feature_cols)
    df_out["Host_CPU_future"] = y.values  # dejamos el target tal cual (sin escalar)

    # Crear carpetas si no existen
    RUTA_CSV_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_SCALER.parent.mkdir(parents=True, exist_ok=True)

    # Guardar CSV preprocesado
    df_out.to_csv(RUTA_CSV_SALIDA, index=False)
    print(f"Archivo preprocesado guardado en: {RUTA_CSV_SALIDA}")

    # Guardar scaler para usarlo luego en predicciones en vivo
    with open(RUTA_SCALER, "wb") as f:
        pickle.dump({"scaler": scaler, "feature_cols": feature_cols}, f)

    print(f"Scaler guardado en: {RUTA_SCALER}")
    print("Columnas usadas como features:", feature_cols)


if __name__ == "__main__":
    main()
