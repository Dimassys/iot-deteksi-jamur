
let sensorChart = null;

// Mengambil elemen HTML
const el = (id) => document.getElementById(id);


// Menentukan status indeks gas
function statusGas(indeks) {
    if (indeks < 30) return "Normal";
    if (indeks < 60) return "Waspada";
    return "Tinggi";
}


// Mengambil data terbaru dari Flask
async function loadLatestData() {
    try {
        const response = await fetch("/api/data");
        const result = await response.json();

        if (result.status !== "success") {
            el("connectionStatus").textContent = "Belum ada data";
            return;
        }

        const data = result.latest;

        const suhu = Number(data.suhu);
        const udara = Number(data.kelembapan_udara);
        const tanah = Number(data.kelembapan_tanah);
        const gas = Number(data.indeks_gas);

        // Kartu sensor utama
        el("suhu").textContent = suhu.toFixed(1) + " °C";
        el("kelembapanUdara").textContent = udara.toFixed(1) + " %";
        el("kelembapanTanah").textContent = tanah.toFixed(1) + " %";
        el("mq135").textContent = gas + " / 100";

        // Status gas
        el("statusGas").textContent = statusGas(gas);
        el("gasStatusDetail").textContent = gas + " / 100";

        // Bar indeks gas
        el("gasMeterFill").style.width =
            Math.max(0, Math.min(100, gas)) + "%";

        // Panel status tambahan
        el("suhuStatus").textContent = suhu.toFixed(1) + " °C";
        el("udaraStatus").textContent = udara.toFixed(1) + " %";
        el("tanahStatus").textContent = tanah.toFixed(1) + " %";

        el("connectionStatus").textContent = "Simulasi Aktif";

    } catch (error) {
        el("connectionStatus").textContent = "Server tidak terhubung";
        console.error("Gagal mengambil data terbaru:", error);
    }
}


// Mengambil riwayat dari Flask
async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const result = await response.json();

        if (result.status !== "success") return;

        const data = result.data;
        const table = el("historyTable");

        if (!data || data.length === 0) {
            table.innerHTML =
                '<tr><td colspan="5">Belum ada data sensor</td></tr>';
            return;
        }

        // Menampilkan data terbaru di bagian atas tabel
        table.innerHTML = data.slice().reverse().map(item => `
            <tr>
                <td>${formatWaktu(item.waktu)}</td>
                <td>${Number(item.suhu).toFixed(1)}</td>
                <td>${Number(item.kelembapan_udara).toFixed(1)}</td>
                <td>${Number(item.kelembapan_tanah).toFixed(1)}</td>
                <td>${Number(item.indeks_gas)} / 100</td>
            </tr>
        `).join("");

        updateChart(data);

    } catch (error) {
        console.error("Gagal mengambil riwayat:", error);
    }
}


// Mengubah waktu menjadi tampilan jam lokal
function formatWaktu(waktu) {
    const date = new Date(waktu);

    if (isNaN(date.getTime())) {
        return waktu;
    }

    return date.toLocaleString("id-ID");
}


// Membuat dan memperbarui grafik
function updateChart(data) {
    const labels = data.map(item => {
        return new Date(item.waktu).toLocaleTimeString("id-ID");
    });

    const suhu = data.map(item => Number(item.suhu));
    const udara = data.map(item => Number(item.kelembapan_udara));
    const tanah = data.map(item => Number(item.kelembapan_tanah));
    const gas = data.map(item => Number(item.indeks_gas));

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: "Suhu (°C)",
                data: suhu,
                borderColor: "#e67e22",
                backgroundColor: "rgba(230,126,34,0.1)",
                tension: 0.3
            },
            {
                label: "Kelembapan Udara (%)",
                data: udara,
                borderColor: "#3498db",
                backgroundColor: "rgba(52,152,219,0.1)",
                tension: 0.3
            },
            {
                label: "Kelembapan Tanah (%)",
                data: tanah,
                borderColor: "#27ae60",
                backgroundColor: "rgba(39,174,96,0.1)",
                tension: 0.3
            },
            {
                label: "Indeks Gas MQ-135",
                data: gas,
                borderColor: "#8e44ad",
                backgroundColor: "rgba(142,68,173,0.1)",
                tension: 0.3
            }
        ]
    };

    if (sensorChart === null) {
        const canvas = el("sensorChart");

        sensorChart = new Chart(canvas, {
            type: "line",
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    mode: "index",
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else {
        sensorChart.data = chartData;
        sensorChart.update("none");
    }
}


// Memperbarui seluruh dashboard
async function refreshDashboard() {
    await loadLatestData();
    await loadHistory();
}


// Menjalankan dashboard
refreshDashboard();

// Refresh setiap 3 detik
setInterval(refreshDashboard, 3000);
