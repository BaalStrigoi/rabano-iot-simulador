import requests
import random
import json
import os
from datetime import datetime

DATABASE_URL = "https://rabano-e4a09-default-rtdb.firebaseio.com"
API_KEY = os.getenv("FIREBASE_API_KEY")

STATE_FILE = "estado.json"
CICLOS_POR_DIA = 96

def cargar_estado():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {
        "contador": 0,
        "humedad_suelo": 76.0,
        "altura_cm": 3.0,
        "numero_hojas": 2,
        "dia_cultivo": 0
    }

def guardar_estado(estado):
    with open(STATE_FILE, "w") as f:
        json.dump(estado, f, indent=2)

def obtener_token():
    if not API_KEY:
        print("No se encontró FIREBASE_API_KEY.")
        return None

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {"returnSecureToken": True}

    r = requests.post(url, json=payload)
    data = r.json()

    if "idToken" in data:
        print("Autenticación anónima correcta.")
        return data["idToken"]

    print("No se pudo autenticar:")
    print(data)
    return None

estado = cargar_estado()
estado["contador"] += 1

# =========================
# CÁLCULO DEL DÍA DE CULTIVO
# =========================
dia_actual = (estado["contador"] - 1) // CICLOS_POR_DIA

# =========================
# TEMPERATURA CUENCA
# =========================
temperatura = random.uniform(17.5, 22.0)

# =========================
# LUMINOSIDAD
# =========================
luminosidad = random.uniform(450, 850)

# =========================
# EVAPORACIÓN DEL SUELO
# =========================
perdida_humedad = random.uniform(0.4, 1.1)

if temperatura > 20:
    perdida_humedad += random.uniform(0.2, 0.5)

estado["humedad_suelo"] -= perdida_humedad

# =========================
# RIEGO AUTOMÁTICO
# =========================
duracion_bombeo = 0
agua_aprox_ml = 0
observaciones = "Condiciones normales"

if estado["humedad_suelo"] < 62:
    duracion_bombeo = random.randint(4, 8)
    agua_aprox_ml = duracion_bombeo * 16
    estado["humedad_suelo"] += random.uniform(10, 16)
    observaciones = "Riego automatico activado"

estado["humedad_suelo"] = max(50, min(85, estado["humedad_suelo"]))

# =========================
# CRECIMIENTO REALISTA DEL RÁBANO
# =========================
# La altura solo cambia una vez al día.
# El registro 1 empieza en 3.0 cm.

if estado["contador"] == 1:
    estado["altura_cm"] = 3.0
    estado["numero_hojas"] = 2
    estado["dia_cultivo"] = 0

elif dia_actual > estado.get("dia_cultivo", 0):
    estado["dia_cultivo"] = dia_actual

    if dia_actual <= 3:
        crecimiento_diario = random.uniform(0.2, 0.4)
    elif dia_actual <= 12:
        crecimiento_diario = random.uniform(0.3, 0.7)
    elif dia_actual <= 25:
        crecimiento_diario = random.uniform(0.2, 0.5)
    else:
        crecimiento_diario = random.uniform(0.05, 0.2)

    estado["altura_cm"] += crecimiento_diario
    estado["altura_cm"] = min(22.0, estado["altura_cm"])

    if estado["numero_hojas"] < 10 and dia_actual % 2 == 0:
        estado["numero_hojas"] += 1

# =========================
# FECHA Y DATOS
# =========================
fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

datos = {
    "registro": estado["contador"],
    "dia_cultivo": estado["dia_cultivo"],
    "fecha_hora": fecha_hora,
    "humedad_suelo_pct": round(estado["humedad_suelo"], 2),
    "duracion_bombeo_seg": duracion_bombeo,
    "agua_aprox_ml": agua_aprox_ml,
    "altura_cm": round(estado["altura_cm"], 2),
    "numero_hojas": estado["numero_hojas"],
    "temperatura_c": round(temperatura, 2),
    "luminosidad_lux": round(luminosidad, 2),
    "observaciones": observaciones
}

token = obtener_token()

ruta = f"{DATABASE_URL}/rabano_datos/registro_{estado['contador']}.json"

if token:
    ruta += f"?auth={token}"

respuesta = requests.put(ruta, json=datos)

print("================================")
print("Registro enviado:", estado["contador"])
print("Día cultivo:", estado["dia_cultivo"])
print("Ruta: rabano_datos/registro_" + str(estado["contador"]))
print("HTTP:", respuesta.status_code)
print("Respuesta Firebase:", respuesta.text)
print(datos)

if respuesta.status_code == 200:
    guardar_estado(estado)
else:
    print("No se guardó estado porque Firebase rechazó el envío.")
