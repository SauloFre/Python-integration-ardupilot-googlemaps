import requests
from pymavlink import mavutil
import time

# =========================
# CONFIGURAÇÕES
# =========================
GOOGLE_API_KEY = "SUA_API_KEY_AQUI"

ARDUPILOT_CONNECTION = "udp:127.0.0.1:14550"  # SITL
ALTITUDE_METERS = 10  # altitude da entrega

# =========================
# GOOGLE MAPS → COORDENADAS
# =========================
def endereco_para_coordenadas(endereco: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"Erro Google Maps: {data['status']}")

    location = data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# =========================
# CONEXÃO COM ARDUPILOT
# =========================
def conectar_ardupilot():
    master = mavutil.mavlink_connection(ARDUPILOT_CONNECTION)
    master.wait_heartbeat()
    print("✅ Conectado ao ArduPilot")
    return master

# =========================
# SETA MODO GUIDED (EXISTE O MODO AUTO, MAS ELE TRABALHA COM UMA MISSÃO PRÉ-DEFINIDA)
# =========================
def set_guided(master):
    master.set_mode_apm("GUIDED")
    time.sleep(2)
    print("🧭 Modo GUIDED ativado")

# =========================
# ENVIA COORDENADAS
# =========================
def enviar_coordenadas(master, lat, lon, alt):
    lat_int = int(lat * 1e7)
    lon_int = int(lon * 1e7)

    master.mav.set_position_target_global_int_send(
        0,
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b110111111000,  # controla posição
        lat_int,
        lon_int,
        alt,
        0, 0, 0,  # velocidade
        0, 0, 0,  # aceleração
        0, 0
    )

    print(f"📍 Enviando drone para: {lat}, {lon}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    endereco = "Av. Paulista, 1000, São Paulo"

    print("🌍 Convertendo endereço em coordenadas...")
    lat, lon = endereco_para_coordenadas(endereco)
    print(f"📌 Coordenadas: {lat}, {lon}")

    drone = conectar_ardupilot()
    set_guided(drone)

    enviar_coordenadas(drone, lat, lon, ALTITUDE_METERS)