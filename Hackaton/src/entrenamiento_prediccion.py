import pandas as pd
from pathlib import Path
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split

# ==============================
# RUTAS
# ==============================
RUTA_CSV_PROCESADO = Path("../data/datos_procesados.csv")
RUTA_MODELO = Path("../models/modelo_prediccion.h5")

TARGET_COL = "Host_CPU_future"


def main():
    print("🔹 Cargando dataset preprocesado...")
    df = pd.read_csv(RUTA_CSV_PROCESADO)

    # ==============================
    # FEATURES Y TARGET
    # ==============================
    X = df.drop(TARGET_COL, axis=1)
    y = df[TARGET_COL]

    # Split entrenamiento / prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        shuffle=True
    )

    print(f"📊 Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    # ==============================
    # MODELO DE PREDICCIÓN
    # ==============================
    model = Sequential([
        Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
        Dense(32, activation="relu"),
        Dense(16, activation="relu"),
        Dense(1)  # Predicción continua (CPU futuro)
    ])

    model.compile(
        optimizer="adam",
        loss="mse",
        metrics=["mae"]
    )

    # Early stopping para evitar overfitting
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    print("🚀 Entrenando modelo de predicción...")
    history = model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=1
    )

    # ==============================
    # EVALUACIÓN
    # ==============================
    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"✅ Evaluación final -> MSE: {loss:.4f} | MAE: {mae:.4f}")

    # ==============================
    # GUARDADO
    # ==============================
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    model.save(RUTA_MODELO)

    print(f"💾 Modelo de predicción guardado en: {RUTA_MODELO}")
    print("🎯 Predicción: Host_CPU a ~1 minuto en el futuro")
    print("🏁 Fase 2 completada correctamente")


if __name__ == "__main__":
    main()
