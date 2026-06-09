const map = L.map("map").setView([-6.3028, 106.8055], 17);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(map);

const gedung = {
    "Lab Komputer": [-6.3025, 106.8042],
    "Kelas A": [-6.3031, 106.8050],
    "Kelas B": [-6.3040, 106.8060],
    "Perpustakaan": [-6.3012, 106.8072],
    "Kantin": [-6.3008, 106.8035],
    "Rektorat": [-6.3050, 106.8085]
};

let markers = [], polylineSegments = [], chart = null;

document.getElementById("runBtn").addEventListener("click", async () => {
    const algo = document.getElementById("algoSelect").value;
    const response = await fetch("/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm: algo })
    });
    const steps = await response.json();
    animateSteps(steps);
});

document.getElementById("exportBtn").addEventListener("click", async () => {
    const algo = document.getElementById("algoSelect").value;
    const response = await fetch("/optimize", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ algorithm: algo }) });
    const steps = await response.json();
    await fetch("/export", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ steps: steps }) })
        .then(resp => resp.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "hasil_simulasi.csv";
            a.click();
        });
});

async function animateSteps(steps) {
    if (chart) chart.destroy();
    const ctx = document.getElementById("distanceChart").getContext("2d");
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(139,92,246,.45)");
    gradient.addColorStop(1, "rgba(139,92,246,0)");
    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{ label: "Total Jarak", data: [], borderColor: "#8b5cf6", backgroundColor: gradient, fill: true, tension: .4, pointRadius: 5, pointHoverRadius: 7 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: "white" } } },
            scales: { x: { ticks: { color: "white" }, grid: { color: "rgba(255,255,255,.06)" } }, y: { ticks: { color: "white" }, grid: { color: "rgba(255,255,255,.06)" } } }
        }
    });

    for (let s = 0; s < steps.length; s++) {
        const step = steps[s];
        polylineSegments.forEach(l => map.removeLayer(l));
        markers.forEach(m => map.removeLayer(m));
        polylineSegments = []; markers = [];

        const route = step.route;
        const coords = route.map(x => gedung[x]);

        for (let i = 0; i < coords.length - 1; i++) {
            const seg = L.polyline([coords[i], coords[i + 1]], { color: "#3b82f6", weight: 5, opacity: 0.8 }).addTo(map);
            polylineSegments.push(seg);
        }

        route.forEach((name, idx) => {
            const marker = L.marker(gedung[name], {
                icon: L.divIcon({ className: "", html: `<div style="width:35px;height:35px;border-radius:50%;background:${step.local_opt ? '#ef4444' : '#2563eb'};display:flex;justify-content:center;align-items:center;font-weight:bold;color:white;border:3px solid white;box-shadow:0 0 15px rgba(59,130,246,.45);">${idx + 1}</div>`, iconSize: [35, 35] })
            }).addTo(map).bindPopup(name);
            markers.push(marker);
        });

        document.getElementById("stepText").innerText = `Iterasi ${s + 1}/${steps.length}`;
        document.getElementById("distanceText").innerText = `${step.distance} meter`;
        chart.data.labels.push(s + 1);
        chart.data.datasets[0].data.push(step.distance);
        chart.update();

        await sleep(700);
    }

    map.fitBounds(L.featureGroup(markers).getBounds());
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }