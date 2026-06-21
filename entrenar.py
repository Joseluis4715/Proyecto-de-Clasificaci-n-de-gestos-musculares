import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import pickle

# Cargar dataset
df = pd.read_csv("dataset.csv")
X = df[["MAV", "RMS", "ZCR", "VAR", "WL", "IEMG"]].values
y = df["gesto"].values

# Dividir en entrenamiento y prueba (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalizar
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# Entrenar SVM
modelo = SVC(kernel="rbf", C=10, gamma="scale")
modelo.fit(X_train, y_train)

# Evaluar
y_pred = modelo.predict(X_test)
print(f"✓ Precisión: {(y_pred == y_test).mean()*100:.1f}%\n")
print(classification_report(y_test, y_pred))
print("Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))

# Guardar modelo
pickle.dump(modelo, open("modelo.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))
print("\n✓ Modelo guardado: modelo.pkl")