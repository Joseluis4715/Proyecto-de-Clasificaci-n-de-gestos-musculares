import numpy as np
import pandas as pd
import glob
import os

def extraer_features(ventana):
    ventana = np.array(ventana, dtype=float)
    mav  = np.mean(np.abs(ventana))
    rms  = np.sqrt(np.mean(ventana ** 2))
    zcr  = np.sum(np.diff(np.sign(ventana)) != 0)
    var  = np.var(ventana)
    wl   = np.sum(np.abs(np.diff(ventana)))
    iemg = np.sum(np.abs(ventana))
    return [mav, rms, zcr, var, wl, iemg]

filas = []
for archivo in glob.glob("datos/*.csv"):
    df = pd.read_csv(archivo)
    for _, fila in df.iterrows():
        señal = fila.iloc[1:].values.astype(float)
        features = extraer_features(señal)
        filas.append([fila["gesto"]] + features)

cols = ["gesto", "MAV", "RMS", "ZCR", "VAR", "WL", "IEMG"]
dataset = pd.DataFrame(filas, columns=cols)
dataset.to_csv("dataset.csv", index=False)

print(f"✓ Dataset generado: {len(dataset)} muestras")
print(dataset.groupby("gesto").size())