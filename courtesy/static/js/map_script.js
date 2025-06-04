document.addEventListener("DOMContentLoaded", async function() {

    const map = L.map("map").setView([53.9, 27.5667], 12);


    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    }).addTo(map);

    const response = await fetch("/api/addresses/")
    const addresses = await response.json()
    console.log(addresses);

addresses.forEach(function (addr) {
    L.marker([addr.latitude, addr.longitude])
        .addTo(map)
        .bindPopup(`<b>${addr.address}</b><br>Время работы: ${addr.working_hours}<br><b>Выходные: сб, вс, праздничные дни</b>`);
});
});