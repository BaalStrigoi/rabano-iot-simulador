import requests
import random
import json
import os
from datetime import datetime

DATABASE_URL = "https://rabano-e4a09-default-rtdb.firebaseio.com"
API_KEY = os.getenv("FIREBASE_API_KEY")

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
        json.dump(estado, f, indent=2)

def obtener_token():
    if not API_KEY:
        print("No se encontró FIREBASE_API_KEY. Se intentará escribir sin auth.")
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

temperatura = random.uniform(17.5, 22.0)
luminosidad = random.uniform(450, 850)

perdida_humedad = random.uniform(0.4, 1.1)

if temperatura > 20:
    perdida_humedad += random.uniform(0.2, 0.5)

estado["humedad_suelo"] -= perdida_humedad

duracion_bombeo = 0
agua_aprox_ml = 0
observaciones = "Condiciones normales"

if estado["humedad_suelo"] < 62:
    duracion_bombeo = random.randint(4, 8)
    agua_aprox_ml = duracion_bombeo * 16
    estado["humedad_suelo"] += random.uniform(10, 16)
    observaciones = "Riego automatico activado"

estado["humedad_suelo"] = max(50, min(85, estado["humedad_suelo"]))

crecimiento = random.uniform(0.02, 0.08)
estado["altura_cm"] += crecimiento
estado["altura_cm"] = min(22.0, estado["altura_cm"])

if estado["contador"] % 12 == 0 and estado["numero_hojas"] < 10:
    estado["numero_hojas"] += 1

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

token = obtener_token()

ruta = f"{DATABASE_URL}/rabano_datos/registro_{estado['contador']}.json"

if token:
    ruta += f"?auth={token}"

respuesta = requests.put(ruta, json=datos)

print("================================")
print("Registro enviado:", estado["contador"])
print("Ruta: rabano_datos/registro_" + str(estado["contador"]))
print("HTTP:", respuesta.status_code)
print("Respuesta Firebase:", respuesta.text)
print(datos)

if respuesta.status_code == 200:
    guardar_estado(estado)
else:
    print("No se guardó estado porque Firebase rechazó el envío.")
