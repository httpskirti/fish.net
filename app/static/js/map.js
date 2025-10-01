// Map Page JavaScript

let map;
let globe;
let currentView = 'researcher';
let currentMapView = '2d'; // '2d' or '3d'
let layers = {
    species: null,
    ocean: null,
    edna: null,
    routes: null,
    heatmap: null
};
let markers = {
    species: [],
    ocean: [],
    edna: [],
    routes: []
};
let globeData = {
    species: [],
    ocean: [],
    edna: [],
    routes: []
};

// Aesthetic map transitions: inject styles and helper animators
const mapEnhanceCSS = `
  .leaflet-tile { opacity: 0; transition: opacity 600ms ease; }
  .leaflet-tile-loaded { opacity: 1 !important; }
  .leaflet-popup { transition: opacity 200ms ease, transform 200ms ease; }
  .leaflet-interactive { transition: filter 200ms ease; }
  .leaflet-interactive:hover { filter: drop-shadow(0 0 8px rgba(0,229,255,0.35)); }
`;
function injectMapEnhanceStyles() {
  if (document.getElementById('map-enhance-styles')) return;
  const s = document.createElement('style');
  s.id = 'map-enhance-styles';
  s.textContent = mapEnhanceCSS;
  document.head.appendChild(s);
}

function createAnimatedCircleMarker(latLng, options, layerGroup, targetRadius, duration = 600) {
  const marker = L.circleMarker(latLng, { ...options, radius: 0 });
  marker.addTo(layerGroup);
  const start = performance.now();
  function step(t) {
    const p = Math.min(1, (t - start) / duration);
    const eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
    marker.setRadius(targetRadius * eased);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
  // Hover enlarge/shrink
  marker.on('mouseover', () => marker.setRadius(targetRadius * 1.25));
  marker.on('mouseout', () => marker.setRadius(targetRadius));
  return marker;
}

function animateGeoJSONLine(geoLayer, duration = 1200) {
  geoLayer.eachLayer((l) => {
    if (l._path) {
      const path = l._path;
      const len = path.getTotalLength ? path.getTotalLength() : 1000;
      path.style.strokeDasharray = `${len}`;
      path.style.strokeDashoffset = `${len}`;
      const start = performance.now();
      function draw(t) {
        const p = Math.min(1, (t - start) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        path.style.strokeDashoffset = `${len * (1 - eased)}`;
        if (p < 1) requestAnimationFrame(draw); else path.style.strokeDasharray = 'none';
      }
      requestAnimationFrame(draw);
    }
  });
}

// Simple measurement state (plugin-free two-click measurement)
let measureState = { active: false, firstLatLng: null, line: null, markers: [] };

// Initialize map page
document.addEventListener('DOMContentLoaded', function() {
    injectMapEnhanceStyles();
    initializeMap();
    loadMapData();
    setupEventListeners();
});

function initializeMap() {
    // Initialize Leaflet map centered on Indian Ocean
    map = L.map('marine-map').setView([15.0, 73.0], 6);

    // Define tile layers
    const openStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    });

    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    // Set default layer
    openStreetMap.addTo(map);

    // Add layer control
    const baseMaps = {
        "Default": openStreetMap,
        "Satellite": satellite
    };

    // Initialize layer groups
    layers.species = L.layerGroup().addTo(map);
    layers.ocean = L.layerGroup().addTo(map);
    layers.edna = L.layerGroup();
    layers.routes = L.layerGroup();
    layers.heatmap = L.heatLayer([], { radius: 25 });

    const overlayMaps = {
        "Species": layers.species,
        "Ocean Data": layers.ocean,
        "eDNA": layers.edna,
        "Routes": layers.routes,
        "Heatmap": layers.heatmap
    };

    L.control.layers(baseMaps, overlayMaps).addTo(map);

    // Initialize Leaflet.draw
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            polyline: true,
            rectangle: true,
            circle: true,
            marker: true
        }
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;
        drawnItems.addLayer(layer);
    });
    
    console.log('Map initialized with drawing tools');
}

function setupEventListeners() {
    // View toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            switchView(view);
        });
    });
    
    // Export form
    const exportForm = document.getElementById('export-form');
    if (exportForm) {
        exportForm.addEventListener('submit', handleExport);
    }
    
    // Depth range sliders
    const depthMin = document.getElementById('depth-min');
    const depthMax = document.getElementById('depth-max');
    
    if (depthMin && depthMax) {
        depthMin.addEventListener('input', updateDepthValues);
        depthMax.addEventListener('input', updateDepthValues);
    }
}

function switchView(view) {
    currentView = view;
    
    // Update toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    // Show/hide appropriate controls
    const researcherControls = document.getElementById('researcher-controls');
    const policymakerControls = document.getElementById('policymaker-controls');
    
    if (view === 'researcher') {
        researcherControls.style.display = 'block';
        policymakerControls.style.display = 'none';
    } else {
        researcherControls.style.display = 'none';
        policymakerControls.style.display = 'block';
    }
    
    // Update map data display based on view
    updateMapForView(view);
}

function updateMapForView(view) {
    if (view === 'policymaker') {
        // Show policy-relevant data
        showProtectedAreas();
        showThreats();
    } else {
        // Show research-relevant data
        hideProtectedAreas();
        hideThreats();
    }
}

async function loadMapData() {
    try {
        const [speciesData, oceanData, ednaData, routesData] = await Promise.all([
            fetch('/api/species/occurrences').then(r => r.json()),
            fetch('/api/ocean/measurements').then(r => r.json()),
            fetch('/api/edna/samples').then(r => r.json()),
            fetch('/api/sea-routes').then(r => r.json())
        ]);

        // Add species markers and heatmap data
        const heatPoints = [];
        speciesData.occurrences.forEach(point => {
            const latLng = [point.latitude, point.longitude];
            heatPoints.push(latLng);

            const targetRadius = Math.max(3, Math.sqrt(point.abundance) * 2);
            const marker = createAnimatedCircleMarker(latLng, {
                fillColor: '#ff6b6b',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }, layers.species, targetRadius);

            marker.bindPopup(`
                <div class="popup-content">
                    <h4>${point.species_name}</h4>
                    <p><strong>Abundance:</strong> ${point.abundance}</p>
                    <p><strong>Date:</strong> ${new Date(point.observed_at).toLocaleDateString()}</p>
                </div>
            `);

            marker.on('click', () => showPointInfo('species', point));
            markers.species.push(marker);
        });

        // Set heatmap data
        layers.heatmap.setLatLngs(heatPoints);

        // Add ocean markers
        oceanData.measurements.forEach(point => {
            const marker = createAnimatedCircleMarker([point.latitude, point.longitude], {
                fillColor: '#4ecdc4',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }, layers.ocean, 8);

            marker.bindPopup(`
                <div class="popup-content">
                    <h4>Ocean Measurement</h4>
                    <p><strong>Temperature:</strong> ${point.temperature}°C</p>
                    <p><strong>Salinity:</strong> ${point.salinity} PSU</p>
                    <p><strong>pH:</strong> ${point.ph}</p>
                </div>
            `);

            marker.on('click', () => showPointInfo('ocean', point));
            markers.ocean.push(marker);
        });

        // Add eDNA markers
        ednaData.samples.forEach(point => {
            const marker = createAnimatedCircleMarker([point.latitude, point.longitude], {
                fillColor: '#45b7d1',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }, layers.edna, 6);

            marker.bindPopup(`
                <div class="popup-content">
                    <h4>eDNA Sample</h4>
                    <p><strong>Species:</strong> ${point.species_name}</p>
                    <p><strong>Confidence:</strong> ${point.confidence}%</p>
                </div>
            `);

            marker.on('click', () => showPointInfo('edna', point));
            markers.edna.push(marker);
        });

        // Add sea routes
        routesData.routes.forEach(route => {
            const routeLayer = L.geoJSON(route.coordinates, {
                style: {
                    color: '#ff7800',
                    weight: 3,
                    opacity: 0.65
                }
            }).addTo(layers.routes);

            routeLayer.bindPopup(`
                <div class="popup-content">
                    <h4>${route.route_name}</h4>
                    <p><strong>Type:</strong> ${route.route_type}</p>
                </div>
            `);

            // Animate route drawing
            animateGeoJSONLine(routeLayer, 1200);

            markers.routes.push(routeLayer);
        });

        updateVisiblePoints();
    } catch (error) {
        console.error('Failed to load map data:', error);
        showNotification('Failed to load map data. Please try again.', 'error');
    }
}

function toggleLayer(layerName) {
    const checkbox = document.getElementById(`${layerName}-layer`);
    const layer = layers[layerName];
    
    if (checkbox.checked) {
        map.addLayer(layer);
    } else {
        map.removeLayer(layer);
    }
    
    updateVisiblePoints();
}

function applyFilters() {
    const speciesFilter = document.getElementById('species-filter').value;
    const timeFilter = document.getElementById('time-filter').value;
    const depthMin = parseInt(document.getElementById('depth-min').value);
    const depthMax = parseInt(document.getElementById('depth-max').value);
    
    // Apply filters to markers (simplified implementation)
    console.log('Applying filters:', { speciesFilter, timeFilter, depthMin, depthMax });
    
    // In a real implementation, you would filter the actual data
    updateVisiblePoints();
}

function updateDepthValues() {
    const depthMin = document.getElementById('depth-min').value;
    const depthMax = document.getElementById('depth-max').value;
    
    document.getElementById('depth-min-val').textContent = depthMin + 'm';
    document.getElementById('depth-max-val').textContent = depthMax + 'm';
}

function updateVisiblePoints() {
    let totalPoints = 0;
    
    Object.keys(layers).forEach(layerName => {
        if (map.hasLayer(layers[layerName])) {
            totalPoints += markers[layerName].length;
        }
    });
    
    document.getElementById('visible-points').textContent = totalPoints;
}

function showPointInfo(type, data) {
    const panel = document.getElementById('data-panel');
    const content = document.getElementById('panel-content');
    
    let html = '';
    
    switch (type) {
        case 'species':
            const sName = data.species_name || data.scientific || data.name || 'Species';
            const sLat = (data.latitude !== undefined ? data.latitude : data.lat);
            const sLng = (data.longitude !== undefined ? data.longitude : data.lng);
            const abundance = (data.abundance !== undefined ? data.abundance : (data.count !== undefined ? data.count : 'N/A'));
            
            // Generate image path from species name
            const imageFileName = sName.toLowerCase().replace(/\s+/g, '_') + '.jpg';
            const imagePath = `/static/images/species/${imageFileName}`;
            
            html = `
                <div class="point-info">
                    <div class="species-image-container">
                        <img src="${imagePath}" alt="${sName}" class="species-image" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="species-image-placeholder" style="display: none;">
                            <i class="fas fa-fish"></i>
                            <span>No image available</span>
                        </div>
                    </div>
                    <h4><i class="fas fa-fish"></i> ${sName}</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Abundance:</span>
                            <span class="info-value">${abundance}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Observed:</span>
                            <span class="info-value">${data.observed_at || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Coordinates:</span>
                            <span class="info-value">${sLat?.toFixed ? sLat.toFixed(3) : sLat}°N, ${sLng?.toFixed ? sLng.toFixed(3) : sLng}°E</span>
                        </div>
                    </div>
                    <div class="point-actions">
                        <button class="btn btn-sm btn-secondary" onclick="exportPointData('species', '${sName}')">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                </div>
            `;
            break;
        case 'ocean':
            const oLat = (data.latitude !== undefined ? data.latitude : data.lat);
            const oLng = (data.longitude !== undefined ? data.longitude : data.lng);
            const temp = (data.temperature !== undefined ? data.temperature : data.temp);
            html = `
                <div class="point-info">
                    <h4><i class="fas fa-water"></i> Ocean Measurement</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Temperature:</span>
                            <span class="info-value">${temp}°C</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Salinity:</span>
                            <span class="info-value">${data.salinity} PSU</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">pH Level:</span>
                            <span class="info-value">${data.ph}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Coordinates:</span>
                            <span class="info-value">${oLat?.toFixed ? oLat.toFixed(3) : oLat}°N, ${oLng?.toFixed ? oLng.toFixed(3) : oLng}°E</span>
                        </div>
                    </div>
                    <div class="point-actions">
                        <button class="btn btn-sm btn-primary" onclick="viewOceanTrends()">
                            <i class="fas fa-chart-line"></i> View Trends
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="exportPointData('ocean', '${oLat}_${oLng}')">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                </div>
            `;
            break;
        case 'edna':
            const eLat = (data.latitude !== undefined ? data.latitude : data.lat);
            const eLng = (data.longitude !== undefined ? data.longitude : data.lng);
            const eSpecies = data.species_name || data.species || 'Species';
            html = `
                <div class="point-info">
                    <h4><i class="fas fa-dna"></i> eDNA Sample</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Species:</span>
                            <span class="info-value">${eSpecies}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Confidence:</span>
                            <span class="info-value">${data.confidence || 'N/A'}%</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Depth:</span>
                            <span class="info-value">${data.depth || 'N/A'}m</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Coordinates:</span>
                            <span class="info-value">${eLat?.toFixed ? eLat.toFixed(3) : eLat}°N, ${eLng?.toFixed ? eLng.toFixed(3) : eLng}°E</span>
                        </div>
                    </div>
                    <div class="point-actions">
                        <button class="btn btn-sm btn-primary" onclick="viewGeneticAnalysis('${eSpecies}')">
                            <i class="fas fa-microscope"></i> Genetic Analysis
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="exportPointData('edna', '${eSpecies}')">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                </div>
            `;
            break;
    }
    
    content.innerHTML = html;
    panel.style.display = 'block';
}

function closeDataPanel() {
    const panel = document.getElementById('data-panel');
    panel.style.display = 'none';
}

// Research tools
function measureDistance() {
    showNotification('Distance tool is now part of the drawing toolbar.', 'info');
}

function drawPolygon() {
    showNotification('Polygon tool is now part of the drawing toolbar.', 'info');
}

function exportMapData() {
    const modal = document.getElementById('export-modal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeExportModal() {
    const modal = document.getElementById('export-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function handleExport(event) {
    event.preventDefault();
    
    const format = document.getElementById('export-format').value;
    const region = document.getElementById('export-region').value;
    const selectedData = Array.from(document.querySelectorAll('input[name="export-data"]:checked'))
        .map(cb => cb.value);
    
    showNotification(`Exporting ${selectedData.join(', ')} data as ${format.toUpperCase()}...`, 'info');
    
    // Simulate export
    setTimeout(() => {
        closeExportModal();
        showNotification('Data exported successfully!', 'success');
    }, 2000);
}

// Policy tools
function showProtectedAreas() {
    showNotification('Displaying protected marine areas', 'info');
    // In a real implementation, you would add protected area overlays
}

function hideProtectedAreas() {
    // Remove protected area overlays
}

function showThreats() {
    showNotification('Displaying threat assessment data', 'warning');
    // In a real implementation, you would add threat indicators
}

function hideThreats() {
    // Remove threat indicators
}

function generateReport() {
    showNotification('Generating policy report...', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        showNotification('Policy report generated successfully!', 'success');
    }, 3000);
}

// Point action functions
function viewSpeciesDetails(scientificName) {
    showNotification(`Loading details for ${scientificName}...`, 'info');
    // In a real implementation, you would navigate to species details
}

function viewOceanTrends() {
    showNotification('Loading ocean parameter trends...', 'info');
    // In a real implementation, you would show trend analysis
}

function viewGeneticAnalysis(species) {
    showNotification(`Loading genetic analysis for ${species}...`, 'info');
    // In a real implementation, you would show genetic data
}

function exportPointData(type, identifier) {
    showNotification(`Exporting ${type} data...`, 'info');
    
    setTimeout(() => {
        showNotification('Point data exported successfully!', 'success');
    }, 1000);
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        'success': '#4caf50',
        'error': '#f44336',
        'warning': '#ff9800',
        'info': '#2196f3'
    };
    return colors[type] || '#2196f3';
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
});

// Handle escape key to close modals
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal[style*="block"]');
        openModals.forEach(modal => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        
        // Also close data panel
        closeDataPanel();
    }
});

// Add CSS for point info styling
const pointInfoStyles = `
    .point-info {
        font-family: var(--font-primary);
    }
    
    .species-image-container {
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .species-image {
        width: 100%;
        max-width: 200px;
        height: 120px;
        object-fit: cover;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 2px solid var(--aqua);
    }
    
    .species-image-placeholder {
        width: 100%;
        max-width: 200px;
        height: 120px;
        background: rgba(0, 188, 212, 0.1);
        border: 2px dashed var(--aqua);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--aqua);
        font-size: 0.9rem;
        margin: 0 auto;
    }
    
    .species-image-placeholder i {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.7;
    }
    
    .point-info h4 {
        color: var(--ocean-blue);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-grid {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background: rgba(0, 188, 212, 0.05);
        border-radius: 4px;
    }
    
    .info-label {
        font-weight: 600;
        color: var(--light-text);
        font-size: 0.9rem;
    }
    
    .info-value {
        font-weight: 500;
        color: var(--dark-text);
    }
    
    .point-actions {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = pointInfoStyles;
document.head.appendChild(styleSheet);

// ============================================================================
// 3D GLOBE FUNCTIONALITY
// ============================================================================

function switchMapView(viewType) {
    currentMapView = viewType;
    
    // Update toggle buttons
    document.querySelectorAll('.map-toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`map-${viewType}-btn`).classList.add('active');
    
    const mapContainer = document.getElementById('marine-map');
    
    if (viewType === '3d') {
        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            showNotification('3D Globe requires Three.js library. Please check your internet connection.', 'error');
            // Revert button state
            document.getElementById('map-2d-btn').classList.add('active');
            document.getElementById('map-3d-btn').classList.remove('active');
            return;
        }
        
        // Hide 2D map
        mapContainer.style.display = 'none';
        
        // Initialize 3D globe
        try {
            initialize3DGlobe();
            showNotification('Switched to 3D Globe view', 'info');
        } catch (error) {
            console.error('Failed to initialize 3D globe:', error);
            showNotification('Failed to load 3D Globe. Switching back to 2D view.', 'error');
            // Revert to 2D
            mapContainer.style.display = 'block';
            document.getElementById('map-2d-btn').classList.add('active');
            document.getElementById('map-3d-btn').classList.remove('active');
        }
    } else {
        // Show 2D map
        mapContainer.style.display = 'block';
        
        // Hide 3D globe
        if (globe && globe.domElement) {
            globe.domElement.style.display = 'none';
        }
        
        // Refresh map
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
        
        showNotification('Switched to 2D Map view', 'info');
    }
}

function initialize3DGlobe() {
    const container = document.querySelector('.map-wrapper');
    
    // Remove existing globe if any
    const existingGlobe = container.querySelector('#globe-container');
    if (existingGlobe) {
        existingGlobe.remove();
    }
    
    // Create globe container
    const globeContainer = document.createElement('div');
    globeContainer.id = 'globe-container';
    globeContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #001122, #003366);
        z-index: 1;
    `;
    container.appendChild(globeContainer);
    
    // Initialize Three.js scene
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x001122, 1);
    globeContainer.appendChild(renderer.domElement);
    
    // Create Earth sphere
    const earthGeometry = new THREE.SphereGeometry(5, 64, 64);
    
    // Load Earth texture (using a simple blue ocean texture)
    const earthTexture = createEarthTexture();
    const earthMaterial = new THREE.MeshPhongMaterial({ 
        map: earthTexture,
        transparent: true,
        opacity: 0.9
    });
    
    const earthMesh = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earthMesh);
    
    // Add atmosphere glow
    const atmosphereGeometry = new THREE.SphereGeometry(5.2, 64, 64);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
        color: 0x4488ff,
        transparent: true,
        opacity: 0.1,
        side: THREE.BackSide
    });
    const atmosphereMesh = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphereMesh);
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    scene.add(directionalLight);
    
    // Position camera
    camera.position.z = 15;
    
    // Add orbit controls (check if available)
    let controls = null;
    if (typeof THREE.OrbitControls !== 'undefined') {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 8;
        controls.maxDistance = 30;
    } else {
        console.warn('OrbitControls not available, using basic camera controls');
    }
    
    // Add data points to globe
    addDataPointsToGlobe(scene);
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate Earth slowly
        earthMesh.rotation.y += 0.002;
        atmosphereMesh.rotation.y += 0.001;
        
        if (controls) {
            controls.update();
        }
        renderer.render(scene, camera);
    }
    animate();
    
    // Handle window resize
    function onWindowResize() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
    window.addEventListener('resize', onWindowResize);
    
    // Store globe reference
    globe = {
        scene: scene,
        camera: camera,
        renderer: renderer,
        controls: controls,
        domElement: globeContainer
    };
}

function createEarthTexture() {
    // Create a simple procedural Earth texture
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Ocean background
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#1e3a8a');
    gradient.addColorStop(0.5, '#1e40af');
    gradient.addColorStop(1, '#1e3a8a');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add some landmass shapes (simplified)
    ctx.fillStyle = '#22c55e';
    
    // Africa/Europe approximation
    ctx.beginPath();
    ctx.ellipse(512, 200, 80, 120, 0, 0, 2 * Math.PI);
    ctx.fill();
    
    // Asia approximation
    ctx.beginPath();
    ctx.ellipse(700, 180, 100, 80, 0, 0, 2 * Math.PI);
    ctx.fill();
    
    // Americas approximation
    ctx.beginPath();
    ctx.ellipse(200, 220, 60, 140, 0, 0, 2 * Math.PI);
    ctx.fill();
    
    return new THREE.CanvasTexture(canvas);
}

function addDataPointsToGlobe(scene) {
    // Convert lat/lng to 3D coordinates and add markers
    const radius = 5.1;
    
    // Add species data points
    markers.species.forEach(marker => {
        if (marker && marker.getLatLng) {
            const latLng = marker.getLatLng();
            const position = latLngTo3D(latLng.lat, latLng.lng, radius);
            
            const pointGeometry = new THREE.SphereGeometry(0.05, 8, 8);
            const pointMaterial = new THREE.MeshBasicMaterial({ color: 0xff6b6b });
            const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);
            
            pointMesh.position.copy(position);
            scene.add(pointMesh);
        }
    });
    
    // Add ocean data points
    markers.ocean.forEach(marker => {
        if (marker && marker.getLatLng) {
            const latLng = marker.getLatLng();
            const position = latLngTo3D(latLng.lat, latLng.lng, radius);
            
            const pointGeometry = new THREE.SphereGeometry(0.04, 8, 8);
            const pointMaterial = new THREE.MeshBasicMaterial({ color: 0x4ecdc4 });
            const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);
            
            pointMesh.position.copy(position);
            scene.add(pointMesh);
        }
    });
    
    // Add eDNA data points
    markers.edna.forEach(marker => {
        if (marker && marker.getLatLng) {
            const latLng = marker.getLatLng();
            const position = latLngTo3D(latLng.lat, latLng.lng, radius);
            
            const pointGeometry = new THREE.SphereGeometry(0.03, 8, 8);
            const pointMaterial = new THREE.MeshBasicMaterial({ color: 0x45b7d1 });
            const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);
            
            pointMesh.position.copy(position);
            scene.add(pointMesh);
        }
    });
}

function latLngTo3D(lat, lng, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);
    
    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const z = (radius * Math.sin(phi) * Math.sin(theta));
    const y = (radius * Math.cos(phi));
    
    return new THREE.Vector3(x, y, z);
}