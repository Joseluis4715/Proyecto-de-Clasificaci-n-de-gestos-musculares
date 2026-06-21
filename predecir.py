import serial
import numpy as np
import pickle
import time
from collections import deque

# Cargar modelo
modelo = pickle.load(open("modelo.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

PUERTO   = "COM12"   # ← cambia al tuyo
BAUDRATE = 115200
FS       = 500
VENTANA  = 2.0      # segundos
N        = int(FS * VENTANA)

EMOJIS = {
    "reposo":       "✋ REPOSO",
    "mano_abierta": "🖐  MANO ABIERTA",
    "giro":         "🔄 GIRO",
    "puno":         "✊ PUÑO"
}

def extraer_features(ventana):
    v = np.array(ventana, dtype=float)
    return [
        np.mean(np.abs(v)),
        np.sqrt(np.mean(v ** 2)),
        np.sum(np.diff(np.sign(v)) != 0),
        np.var(v),
        np.sum(np.abs(np.diff(v))),
        np.sum(np.abs(v))
    ]

print("=== Predicción en tiempo real ===")
print(f"Conectando a {PUERTO}...")

ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
time.sleep(2)
ser.flushInput()

print("✓ Conectado. Haz un gesto y mantén 2 segundos.\n")
print("Ctrl+C para salir\n")

buffer = deque(maxlen=N)

try:
    while True:
        linea = ser.readline().decode("utf-8", errors="ignore").strip()
        if not linea.startswith(">EMG:"):
            continue
        try:
            valor = int(linea.split(":")[1])
        except:
            continue

        buffer.append(valor)

        if len(buffer) == N:
            features = extraer_features(list(buffer))
            features_scaled = scaler.transform([features])
            gesto = modelo.predict(features_scaled)[0]
            label = EMOJIS.get(gesto, gesto)
            print(f"\r→ {label}          ", end="", flush=True)
            buffer.clear()

except KeyboardInterrupt:
    print("\n\nSaliendo...")
    ser.close()