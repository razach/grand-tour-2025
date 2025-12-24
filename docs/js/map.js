document.addEventListener('DOMContentLoaded', () => {

    // Initialize map
    const map = L.map('map', {
        scrollWheelZoom: false,
    }).setView([36.2, -85.5], 7);

    // Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Explicitly define icon to avoid 404s
    const goldIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Coordinates
    const Atlanta = [33.7490, -84.3880];
    const Chat = [35.0456, -85.3097];
    const Nashville = [36.1627, -86.7816];
    const Bardstown = [37.8092, -85.4669];
    const Louisville = [38.2527, -85.7585];
    const Knoxville = [35.9606, -83.9207];

    const stops = [
        { coords: Atlanta, title: "Atlanta (Start/End)", desc: "Home Base" },
        { coords: Chat, title: "Chattanooga", desc: "Supercharger & Lunch Stop" },
        { coords: Nashville, title: "Nashville", desc: "Night 1: Broadway & Tunes" },
        { coords: Bardstown, title: "Bardstown", desc: "Bourbon Capital" },
        { coords: Louisville, title: "Louisville", desc: "Urban Bourbon Trail" },
        { coords: Knoxville, title: "Knoxville", desc: "The Scenic Return" }
    ];

    stops.forEach(stop => {
        L.marker(stop.coords, { icon: goldIcon }).addTo(map)
            .bindPopup(`<b>${stop.title}</b><br>${stop.desc}`);
    });

    // Route Line
    const routeLatLongs = [Atlanta, Chat, Nashville, Bardstown, Louisville, Knoxville, Chat, Atlanta];

    const routeLine = L.polyline(routeLatLongs, {
        color: '#d4Af37',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 10',
        lineCap: 'round'
    }).addTo(map);

    map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
});
