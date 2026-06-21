# servidor.py — EMG Dino Game Backend
# Lee señal del ESP32, detecta gesto con el modelo entrenado
# y lo transmite al navegador por WebSocket

import asyncio
import websockets
import serial
import numpy as np
import pickle
import json
import time
from collections import deque

# ── Configuración ──────────────────────────────────────────
PUERTO   = "COM12"       # ← cambia al tuyo
BAUDRATE = 115200
FS       = 500
VENTANA  = 1.0          # igual que en recolectar.py — CRÍTICO
N        = int(FS * VENTANA)
WS_PORT  = 8765

# ── Cargar modelo ──────────────────────────────────────────
try:
    modelo = pickle.load(open("modelo.pkl", "rb"))
    scaler = pickle.load(open("scaler.pkl", "rb"))
    print("✓ Modelo cargado")
except:
    print("✗ No se encontró modelo.pkl — corre primero entrenar.py")
    exit()

# ── Extraer features ───────────────────────────────────────
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

# ── Estado global ──────────────────────────────────────────
clientes = set()
gesto_actual = "reposo"

async def broadcast(mensaje):
    if clientes:
        await asyncio.gather(*[c.send(mensaje) for c in clientes])

async def handler(websocket):
    clientes.add(websocket)
    print(f"✓ Navegador conectado ({len(clientes)} clientes)")
    # Enviar el gesto actual al nuevo cliente inmediatamente
    try:
        await websocket.send(json.dumps({"gesto": gesto_actual}))
    except:
        pass
    try:
        await websocket.wait_closed()
    finally:
        clientes.discard(websocket)

async def leer_serial():
    global gesto_actual
    print(f"Conectando a {PUERTO}...")
    try:
        ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
        print(f"✓ ESP32 conectado en {PUERTO}")
    except Exception as e:
        print(f"✗ Error puerto serial: {e}")
        return

    await asyncio.sleep(2)
    ser.flushInput()
    buffer = deque(maxlen=N)

    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="ignore").strip()
            if not linea.startswith(">EMG:"):
                continue
            valor = int(linea.split(":")[1])
            buffer.append(valor)

            if len(buffer) == N:
                features = extraer_features(list(buffer))
                fs = scaler.transform([features])
                gesto = modelo.predict(fs)[0]
                gesto_actual = gesto
                msg = json.dumps({"gesto": gesto})
                await broadcast(msg)
                print(f"→ {gesto}")

                buffer.clear()

        except Exception as e:
            await asyncio.sleep(0.01)

async def main():
    print("=== EMG Dino Server ===")
    print(f"WebSocket en ws://localhost:{WS_PORT}")
    print("Abre juego.html en el navegador\n")

    server = await websockets.serve(handler, "0.0.0.0", WS_PORT)
    await asyncio.gather(server.wait_closed(), leer_serial())

if __name__ == "__main__":
    asyncio.run(main())