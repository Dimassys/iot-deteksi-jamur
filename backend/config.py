
import os
from dotenv import load_dotenv

# Membaca file .env jika tersedia (untuk penggunaan lokal)
load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC",
    "deteksi_jamur/pohon1/telemetry"
)
MQTT_CLIENT_ID = os.getenv(
    "MQTT_CLIENT_ID",
    "rubberguard_backend"
)
