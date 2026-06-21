import serial
import csv
import time
import os

PUERTO   = "COM12"    # ← cambia esto al puerto de tu ESP32
BAUDRATE = 115200
VENTANA  = 2.0       # segundos por muestra
MUESTRAS = 20        # repeticiones por gesto
FS       = 500       # Hz

GESTOS = {
    "1": "reposo",
    "2": "mano_abierta",
    "3": "giro",
    "4": "puno"
}

os.makedirs("datos", exist_ok=True)
ser = serial.Serial(PUERTO, BAUDRATE, timeout=1)
time.sleep(2)

print("=== Recolector EMG ===")
print("1=reposo | 2=mano_abierta | 3=giro | 4=puno | q=salir\n")

while True:
    tecla = input("Gesto a grabar: ").strip()
    if tecla == "q":
        break
    if tecla not in GESTOS:
        print("Tecla inválida")
        continue

    gesto = GESTOS[tecla]
    archivo = f"datos/{gesto}.csv"
    modo = "a" if os.path.exists(archivo) else "w"

    with open(archivo, modo, newline="") as f:
        writer = csv.writer(f)
        if modo == "w":
            writer.writerow(["gesto"] + [f"t{i}" for i in range(int(FS * VENTANA))])

        for rep in range(1, MUESTRAS + 1):
            input(f"  [{rep}/{MUESTRAS}] Prepara '{gesto}' → ENTER para grabar...")
            print("  Grabando...", end=" ", flush=True)

            muestras = []
            inicio = time.time()
            ser.flushInput()

            while time.time() - inicio < VENTANA:
                linea = ser.readline().decode("utf-8", errors="ignore").strip()
                if linea.startswith(">EMG:"):
                    try:
                        muestras.append(int(linea.split(":")[1]))
                    except:
                        pass

            n = int(FS * VENTANA)
            if len(muestras) >= n:
                muestras = muestras[:n]
            else:
                muestras += [0] * (n - len(muestras))

            writer.writerow([gesto] + muestras)
            print(f"✓ ({len([x for x in muestras if x != 0])} puntos)")

ser.close()
print("\nDatos guardados en /datos/")