import json
import ssl
import paho.mqtt.client as mqtt

from backend.config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC
)

# Membuat MQTT client pengirim
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="python_test_publish"
)

# Mengatur username dan password
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Mengaktifkan TLS
client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

# Menghubungkan ke CloudAMQP
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

# Data sensor simulasi
data = {
    "device_id": "ESP32_JAMUR_01",
    "suhu": 29.5,
    "kelembapan_udara": 80,
    "kelembapan_tanah": 65,
    "mq135": 820
}

# Mengirim data ke broker
result = client.publish(
    MQTT_TOPIC,
    json.dumps(data),
    qos=1
)

result.wait_for_publish()

print("Data berhasil dikirim:")
print(json.dumps(data, indent=4))

# Memutuskan koneksi
client.loop_stop()
client.disconnect()