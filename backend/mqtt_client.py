
import json
import ssl
import time

import paho.mqtt.client as mqtt

from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC,
    MQTT_CLIENT_ID
)

from csv_logger import save_sensor_data


# Status koneksi MQTT
mqtt_connected = False


# Fungsi ketika Python berhasil terhubung ke CloudAMQP
def on_connect(client, userdata, flags, reason_code, properties):
    global mqtt_connected

    if reason_code == 0:
        mqtt_connected = True

        print("\n===================================")
        print("BERHASIL TERHUBUNG KE CLOUDAMQP")
        print("===================================")

        print("Broker :", MQTT_HOST)
        print("Topic  :", MQTT_TOPIC)

        # Berlangganan ke topik data sensor ESP32
        client.subscribe(MQTT_TOPIC)

        print("Menunggu data dari ESP32...\n")

    else:
        mqtt_connected = False
        print("Koneksi MQTT gagal. Kode:", reason_code)


# Fungsi ketika koneksi MQTT terputus
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    global mqtt_connected

    mqtt_connected = False

    print("Koneksi MQTT terputus. Kode:", reason_code)


# Fungsi ketika Python menerima pesan dari ESP32
def on_message(client, userdata, message):

    try:
        # Mengubah data byte menjadi teks
        raw_data = message.payload.decode("utf-8")

        # Mengubah teks JSON menjadi dictionary Python
        payload = json.loads(raw_data)

        print("\n========== DATA SENSOR DITERIMA ==========")
        print("Topic :", message.topic)
        print("Data  :", payload)

        # Memastikan data berbentuk objek JSON
        if not isinstance(payload, dict):
            print("Data ditolak: format JSON harus berupa objek.")
            return

        # Memeriksa keberadaan seluruh parameter sensor
        required_fields = [
            "suhu",
            "kelembapan_udara",
            "kelembapan_tanah",
            "mq135"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in payload
        ]

        if missing_fields:
            print("Data ditolak. Parameter tidak ditemukan:", missing_fields)
            return

        # Memastikan nilai sensor berupa angka
        for field in required_fields:
            value = payload[field]

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                print(f"Data ditolak: {field} harus berupa angka.")
                return

        # Menyimpan data sensor ke CSV
        save_sensor_data(payload)

        print("==========================================\n")

    except json.JSONDecodeError:
        print("Pesan ditolak: format JSON tidak valid.")

    except UnicodeDecodeError:
        print("Pesan ditolak: data bukan teks UTF-8.")

    except Exception as error:
        print("Terjadi kesalahan saat memproses data:", error)


# Membuat dan mengatur koneksi MQTT
def create_mqtt_client():

    # Membuat objek MQTT Client menggunakan callback API versi 2
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311
    )

    # Mengatur username dan password CloudAMQP
    client.username_pw_set(
        MQTT_USERNAME,
        MQTT_PASSWORD
    )

    # Mengaktifkan TLS untuk port 8883
    client.tls_set(
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )

    # Mengatur fungsi callback
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    return client


# Fungsi utama untuk menjalankan MQTT
def start_mqtt():

    client = create_mqtt_client()

    print("Menghubungkan ke CloudAMQP...")
    print("Broker:", MQTT_HOST)

    try:
        # Menghubungkan ke broker CloudAMQP
        client.connect(
            MQTT_HOST,
            MQTT_PORT,
            keepalive=60
        )

        # Menjalankan loop MQTT agar pesan terus diterima
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nProgram MQTT dihentikan.")

    except Exception as error:
        print("Kesalahan koneksi MQTT:", error)

    finally:
        client.disconnect()


# Menjalankan program jika file dieksekusi langsung
if __name__ == "__main__":
    start_mqtt()
