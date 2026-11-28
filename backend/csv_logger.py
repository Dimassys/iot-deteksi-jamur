import csv
import json
from datetime import datetime
from pathlib import Path

from config import CSV_FILE


# Kolom yang akan disimpan ke dalam CSV
CSV_COLUMNS = [
    "waktu",
    "device_id",
    "suhu",
    "kelembapan_udara",
    "kelembapan_tanah",
    "mq135"
]


def save_sensor_data(payload):
    """
    Menyimpan satu data pengukuran sensor ke file CSV.

    payload: data JSON yang diterima dari ESP32.
    """

    # Memastikan folder penyimpanan tersedia
    Path(CSV_FILE).parent.mkdir(parents=True, exist_ok=True)

    # Memeriksa apakah file CSV sudah tersedia
    file_exists = Path(CSV_FILE).exists()

    # Menyiapkan satu baris data
    row = {
        "waktu": datetime.now().astimezone().isoformat(timespec="seconds"),
        "device_id": payload.get("device_id", "ESP32_JAMUR_01"),
        "suhu": payload.get("suhu", ""),
        "kelembapan_udara": payload.get("kelembapan_udara", ""),
        "kelembapan_tanah": payload.get("kelembapan_tanah", ""),
        "mq135": payload.get("mq135", "")
    }

    # Menambahkan data ke file CSV
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)

        # Membuat header hanya jika file belum ada
        if not file_exists or Path(CSV_FILE).stat().st_size == 0:
            writer.writeheader()

        writer.writerow(row)

    print("Data sensor berhasil disimpan ke CSV:", row)


def get_latest_data():
    """
    Mengambil satu baris data sensor paling terbaru dari CSV.
    Digunakan untuk menampilkan data terakhir pada dashboard.
    """

    if not Path(CSV_FILE).exists():
        return None

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        latest = None

        for row in reader:
            latest = row

        return latest


def get_all_data():
    """
    Mengambil seluruh riwayat pengukuran dari CSV.
    """

    if not Path(CSV_FILE).exists():
        return []

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)