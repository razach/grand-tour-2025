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
    // Coordinates
    const Atlanta = [33.7490, -84.3880];
    const Chat = [35.0456, -85.3097];
    const Lynchburg = [35.2828, -86.3678]; // Jack Daniel's
    const Nashville = [36.1627, -86.7816];
    const Clermont = [37.9304, -85.6558]; // Jim Beam
    const Bardstown = [37.8092, -85.4669];
    const Louisville = [38.2527, -85.7585];
    const Frankfort = [38.2009, -84.8733]; // Buffalo Trace / Castle & Key
    const Versailles = [38.0464, -84.7231]; // Woodford Reserve
    const Knoxville = [35.9606, -83.9207];

    const stops = [
        { coords: Atlanta, title: "Atlanta", desc: "Start/End" },
        { coords: Chat, title: "Chattanooga", desc: "Supercharger Stop" },
        { coords: Lynchburg, title: "Jack Daniel's", desc: "Lynchburg, TN" },
        { coords: Nashville, title: "Nashville", desc: "Night 1" },
        { coords: Clermont, title: "Jim Beam", desc: "Clermont, KY" },
        { coords: Bardstown, title: "Bardstown", desc: "Heaven Hill" },
        { coords: Louisville, title: "Louisville", desc: "Nights 2 & 3" },
        { coords: Frankfort, title: "Frankfort", desc: "Buffalo Trace & Castle/Key" },
        { coords: Versailles, title: "Woodford Reserve", desc: "Versailles, KY" },
        { coords: Knoxville, title: "Knoxville", desc: "Return Trip" }
    ];

    stops.forEach(stop => {
        L.marker(stop.coords, { icon: goldIcon }).addTo(map)
            .bindPopup(`<b>${stop.title}</b><br>${stop.desc}`);
    });

    // Route Line
    const routeLatLongs = [
        Atlanta, Chat, Lynchburg, Nashville, // Day 1
        Clermont, Bardstown, Louisville, // Day 2
        Frankfort, Versailles, Louisville, // Day 3
        Knoxville, Chat, Atlanta // Day 4
    ];

    const routeLine = L.polyline(routeLatLongs, {
        color: '#d4Af37',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 10',
        lineCap: 'round'
    }).addTo(map);

    map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
});
