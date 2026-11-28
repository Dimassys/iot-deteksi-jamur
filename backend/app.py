
from flask import Flask, render_template, jsonify, send_file
from pathlib import Path
from datetime import datetime
import csv
import random
import time

app = Flask(__name__)

# Lokasi penyimpanan CSV
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_FILE = DATA_DIR / "sensor_data.csv"

DATA_DIR.mkdir(exist_ok=True)

CSV_HEADER = [
    "waktu",
    "device_id",
    "suhu",
    "kelembapan_udara",
    "kelembapan_tanah",
    "indeks_gas"
]

# Data simulasi awal
sensor_data = {
    "device_id": "ESP32_JAMUR_01",
    "suhu": 29.5,
    "kelembapan_udara": 80.0,
    "kelembapan_tanah": 65.0,
    "indeks_gas": 18
}

last_update = time.time()


# Membuat file CSV jika belum tersedia
def buat_csv():
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)


# Menyimpan data sensor ke CSV
def simpan_csv(data):
    buat_csv()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            data["waktu"],
            data["device_id"],
            data["suhu"],
            data["kelembapan_udara"],
            data["kelembapan_tanah"],
            data["indeks_gas"]
        ])


# Membaca seluruh riwayat CSV
def baca_csv():
    buat_csv()

    hasil = []

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                hasil.append({
                    "waktu": row["waktu"],
                    "device_id": row["device_id"],
                    "suhu": float(row["suhu"]),
                    "kelembapan_udara": float(row["kelembapan_udara"]),
                    "kelembapan_tanah": float(row["kelembapan_tanah"]),
                    "indeks_gas": int(float(row["indeks_gas"]))
                })
            except (ValueError, KeyError):
                continue

    return hasil


# Membuat data simulasi untuk preview dashboard
def buat_data_simulasi():
    global last_update

    sekarang = time.time()

    # Membuat data baru setiap 3 detik
    if sekarang - last_update >= 3:

        sensor_data["suhu"] = round(
            max(24, min(36, sensor_data["suhu"] + random.uniform(-0.4, 0.4))),
            1
        )

        sensor_data["kelembapan_udara"] = round(
            max(50, min(98, sensor_data["kelembapan_udara"] + random.uniform(-1.5, 1.5))),
            1
        )

        sensor_data["kelembapan_tanah"] = round(
            max(20, min(95, sensor_data["kelembapan_tanah"] + random.uniform(-1, 1))),
            1
        )

        sensor_data["indeks_gas"] = max(
            0,
            min(100, sensor_data["indeks_gas"] + random.randint(-3, 3))
        )

        last_update = sekarang

        data_baru = {
            "waktu": datetime.now().astimezone().isoformat(timespec="seconds"),
            **sensor_data
        }

        simpan_csv(data_baru)

    return {
        "waktu": datetime.now().astimezone().isoformat(timespec="seconds"),
        **sensor_data
    }


# Halaman utama dashboard
@app.route("/")
def index():
    return render_template("index.html")


# API data sensor terbaru
@app.route("/api/data")
def api_data():
    data = buat_data_simulasi()

    return jsonify({
        "status": "success",
        "latest": data
    })


# API riwayat sensor
@app.route("/api/history")
def api_history():
    data = baca_csv()

    return jsonify({
        "status": "success",
        "data": data[-100:]
    })


# Download data sensor dalam bentuk CSV
@app.route("/download/csv")
def download_csv():
    buat_csv()

    return send_file(
        CSV_FILE,
        as_attachment=True,
        download_name="data_sensor_jamur.csv",
        mimetype="text/csv"
    )


if __name__ == "__main__":
    buat_csv()

    print("====================================")
    print(" RUBBERGUARD IOT - MODE SIMULASI")
    print("====================================")
    print("Dashboard: http://localhost:5000")
    print("Data sensor: SIMULASI")
    print("CSV:", CSV_FILE)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
