document.addEventListener('DOMContentLoaded', () => {

    // Fix Leaflet's default icon path issues
    delete L.Icon.Default.prototype._getIconUrl;

    L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    });

    // Initialize map centered on the region
    const map = L.map('map', {
        scrollWheelZoom: false, // Prevent scrolling page from zooming map
    }).setView([36.2, -85.5], 7); // Center roughly between ATL and Louisville

    // Add Dark Mode Tiles (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Coordinates
    const Atlanta = [33.7490, -84.3880];
    const Chat = [35.0456, -85.3097];
    const Nashville = [36.1627, -86.7816];
    const Bardstown = [37.8092, -85.4669];
    const Louisville = [38.2527, -85.7585];
    const Knoxville = [35.9606, -83.9207];

    // Markers (Custom Gold Color if possible, but default blue for now is fine, we can style popup)
    const stops = [
        { coords: Atlanta, title: "Atlanta (Start/End)", desc: "Home Base" },
        { coords: Chat, title: "Chattanooga", desc: "Supercharger & Lunch Stop" },
        { coords: Nashville, title: "Nashville", desc: "Night 1: Broadway & Tunes" },
        { coords: Bardstown, title: "Bardstown", desc: "Bourbon Capital" },
        { coords: Louisville, title: "Louisville", desc: "Urban Bourbon Trail" },
        { coords: Knoxville, title: "Knoxville", desc: "The Scenic Return" }
    ];

    stops.forEach(stop => {
        L.marker(stop.coords).addTo(map)
            .bindPopup(`<b>${stop.title}</b><br>${stop.desc}`);
    });

    // Draw the Route (Approximate Lines)
    const routeLatLongs = [
        Atlanta,
        Chat,
        Nashville,
        Bardstown,
        Louisville,
        Knoxville,
        Chat, // Closing the loop roughly
        Atlanta
    ];

    const routeLine = L.polyline(routeLatLongs, {
        color: '#d4Af37', // Bourbon Gold
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 10', // Dashed line for "Road Trip" vibe
        lineCap: 'round'
    }).addTo(map);

    // Adjust view to fit route
    map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
});
