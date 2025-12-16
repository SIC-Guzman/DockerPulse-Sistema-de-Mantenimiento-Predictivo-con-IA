import pandas as pd
from pathlib import Path
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split

RUTA_CSV_PROCESADO = Path("DockerPulse/datos_procesados.csv")
RUTA_MODELO = Path("models/modelo_prediccion.h5")

def main():
    df = pd.read_csv(RUTA_CSV_PROCESADO)

    # X = todas las columnas menos la columna objetivo
    X = df.drop("Host_CPU_future", axis=1)
    y = df["Host_CPU_future"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Sequential([
        Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
        Dense(32, activation="relu"),
        Dense(16, activation="relu"),
        Dense(1)  # Predice un valor continuo: Host_CPU_future
    ])

    model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    history = model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1
    )

    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"Loss (MSE): {loss:.4f}  |  MAE: {mae:.4f}")

    # Crear carpeta models si no existe
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    model.save(RUTA_MODELO)
    print(f"Modelo guardado en: {RUTA_MODELO}")


if __name__ == "__main__":
    main()
