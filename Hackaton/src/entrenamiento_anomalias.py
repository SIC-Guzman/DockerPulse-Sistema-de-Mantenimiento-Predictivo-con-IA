import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path
import pickle

# ==============================
# RUTAS
# ==============================
RUTA_CSV = Path("../data/datos_procesados.csv")
RUTA_MODELO = Path("../models/modelo_anomalia.pkl")

TARGET_COL = "Host_CPU_future"


def main():
    print("🔹 Cargando datos procesados...")
    df = pd.read_csv(RUTA_CSV)

    # ==============================
    # FEATURES (sin la variable futura)
    # ==============================
    X = df.drop(TARGET_COL, axis=1)

    # ==============================
    # MODELO DE ANOMALÍAS
    # ==============================
    print("🚨 Entrenando modelo Isolation Forest...")
    modelo_anomalia = IsolationForest(
        n_estimators=200,
        contamination=0.03,   # ~3% de comportamientos raros
        random_state=42
    )

    modelo_anomalia.fit(X)

    # ==============================
    # GUARDADO
    # ==============================
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_MODELO, "wb") as f:
        pickle.dump(
            {
                "model": modelo_anomalia,
                "feature_cols": list(X.columns)
            },
            f
        )

    print(f"💾 Modelo de anomalías guardado en: {RUTA_MODELO}")

    # ==============================
    # VALIDACIÓN RÁPIDA
    # ==============================
    preds = modelo_anomalia.predict(X)
    df_result = pd.DataFrame({"anomalia": preds})

    print("\n📊 Resultados de detección:")
    print(df_result["anomalia"].value_counts())

    print("\nℹ️  Nota:")
    print("  1  -> Comportamiento normal")
    print(" -1  -> Anomalía detectada")
    print("🏁 Fase 3 completada correctamente")


if __name__ == "__main__":
    main()
