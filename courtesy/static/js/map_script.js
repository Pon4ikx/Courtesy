document.addEventListener("DOMContentLoaded", async function() {
    // Инициализация карты
    const map = L.map("map").setView([53.9, 27.5667], 12); // Центр карты (Минск)

    // Добавление слоя OpenStreetMap
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    }).addTo(map);

    const response = await fetch("/api/addresses/")
    const addresses = await response.json()
    console.log(addresses);

// Добавление маркеров на карту
addresses.forEach(function (addr) {
    // str = 
    L.marker([addr.latitude, addr.longitude])
        .addTo(map)
        .bindPopup(`<b>${addr.address}</b><br>Время работы: ${addr.working_hours}`);
});
});