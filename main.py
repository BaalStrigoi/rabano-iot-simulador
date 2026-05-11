import requests
import random
import json
import os
from datetime import datetime

DATABASE_URL = "https://rabano-e4a09-default-rtdb.firebaseio.com"

STATE_FILE = "estado.json"

def cargar_estado():

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    return {
        "contador": 0,
        "humedad_suelo": 76.0,
        "altura_cm": 5.5,
        "numero_hojas": 5
    }

def guardar_estado(estado):

    with open(STATE_FILE, "w") as f:
        json.dump(estado, f)

estado = cargar_estado()

estado["contador"] += 1

# =========================
# TEMPERATURA CUENCA
# =========================
temperatura = random.uniform(17.5, 22.0)

# =========================
# LUMINOSIDAD
# =========================
luminosidad = random.uniform(450, 850)

# =========================
# EVAPORACIÓN REALISTA
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
# CRECIMIENTO REAL DEL RÁBANO
# =========================

crecimiento = random.uniform(0.02, 0.08)

estado["altura_cm"] += crecimiento

# altura máxima razonable
estado["altura_cm"] = min(22.0, estado["altura_cm"])

# hojas crecen lento
if estado["contador"] % 12 == 0 and estado["numero_hojas"] < 10:
    estado["numero_hojas"] += 1

# =========================
# FECHA
# =========================
fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

datos = {
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

ruta = f"{DATABASE_URL}/rabano/registros/registro_{estado['contador']}.json"

respuesta = requests.put(ruta, json=datos)

print("================================")
print("Registro enviado:", estado["contador"])
print("HTTP:", respuesta.status_code)
print(datos)

guardar_estado(estado)
