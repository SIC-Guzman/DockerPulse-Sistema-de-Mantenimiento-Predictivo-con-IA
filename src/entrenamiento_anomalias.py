import pandas as pd
from sklearn.cluster import KMeans
from pathlib import Path
import pickle

# Rutas
RUTA_CSV = Path("DockerPulse/datos_procesados.csv")
RUTA_MODELO = Path("models/modelo_anomalia.pkl")

def main():
    print("Cargando datos procesados...")
    df = pd.read_csv(RUTA_CSV)

    # Todas las columnas excepto la columna objetivo (Host_CPU_future)
    X = df.drop("Host_CPU_future", axis=1)

    print("Entrenando modelo K-Means (2 clusters)...")
    kmeans = KMeans(n_clusters=2, random_state=42)
    kmeans.fit(X)

    # Guardamos el modelo entrenado
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_MODELO, "wb") as f:
        pickle.dump(kmeans, f)

    print(f"Modelo de anomalías guardado en: {RUTA_MODELO}")

    # Mostrar distribución de clusters
    clusters = kmeans.predict(X)
    df_clusters = pd.DataFrame({"cluster": clusters})
    print("\nDistribución de clusters:")
    print(df_clusters["cluster"].value_counts())


if __name__ == "__main__":
    main()
