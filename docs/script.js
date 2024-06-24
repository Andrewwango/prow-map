let map = L.map( 'map', {
    center: [52.067137963027754, -0.39834061887875316],
    minZoom: 10,
    maxZoom: 16,
    zoom: 12
});

// Leaflet map
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', { //{s}.tile.openstreetmap.org
    attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright/" target="_blank">OpenStreetMap</a>',
}).addTo(map);

// Plot paths
async function populateMap(clean_edge_list_json_file) {
    try {
        const response = await fetch(clean_edge_list_json_file);
        const data = await response.json();

        data.edge_list.forEach(edge => {
            let polyline = L.polyline(edge.geometry, { color: edge.color }).addTo(map);
            polyline.on('mouseover', function (e) {
                this.setStyle({weight: 8});
            });
    
            polyline.on('mouseout', function (e) {
                this.setStyle({weight: 3});
            });
        });
    } catch (error) {
        console.error('Error:', error);
        return "";
    }
}

function onStartup() {
    populateMap('geojsons/Beds_EO.geojson');
}

// Legend
let legend = L.control({ position: 'topright' });

legend.onAdd = function (map) {
  let div = L.DomUtil.create('div', 'legend');
  div.innerHTML += '<i style="background: black"></i> Public Right of Way<br>';
  div.innerHTML += '<i style="background: magenta"></i> Active non-PRoW<br>';
  div.innerHTML += '<i style="background: red"></i> Highly active non-PRoW<br>';
  return div;
};

legend.addTo(map);

// Boundaries
fetch('boundaries/lad_filtered.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            invert: true,
            renderer: L.svg({ padding: 1 }),
            style: {
                color: "blue",      // Boundary color
                weight: 2,          // Boundary weight
                fillColor: "black", // Fill color
                fillOpacity: 0.1    // Fill opacity
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error loading the GeoJSON file:', error));
