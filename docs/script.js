let map = L.map( 'map', {
    center: [52.067137963027754, -0.39834061887875316],
    minZoom: 10,
    maxZoom: 16,
    zoom: 12
});

L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', { //{s}.tile.openstreetmap.org
    attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright/" target="_blank">OpenStreetMap</a>',
}).addTo(map);

async function populateMap(clean_edge_list_json_file) {
    try {
        const response = await fetch(clean_edge_list_json_file);
        const data = await response.json();

        data.edge_list.forEach(edge => {
            L.polyline(edge.geometry, { color: edge.color }).addTo(map);
        });
    } catch (error) {
        console.error('Error:', error);
        return "";
    }
}

function onStartup() {
    populateMap('../output/Beds_EO.json');
}