// Researcher Dashboard JavaScript

let researchMap;
let speciesChart, oceanChart, ednaChart;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Researcher Dashboard loaded');
    initializeResearcherDashboard();
});

function initializeResearcherDashboard() {
    loadDashboardData();
    initializeMap();
    initializeCharts();
    setupEventListeners();
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load summary statistics
        const response = await fetch('/api/data/researcher/summary');
        if (response.ok) {
            const data = await response.json();
            updateStatistics(data);
        } else {
            // Use mock data for demo
            updateStatistics(getMockResearcherData());
        }
        
        // Load recent data
        loadRecentData();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Use mock data as fallback
        updateStatistics(getMockResearcherData());
        loadRecentData();
    }
}

function updateStatistics(data) {
    document.getElementById('total-species').textContent = data.species_count || '10';
    document.getElementById('ocean-datapoints').textContent = data.ocean_datapoints || '15';
    document.getElementById('edna-samples').textContent = data.edna_samples || '15';
    document.getElementById('avg-diversity').textContent = data.avg_diversity || '2.67';
    
    document.getElementById('threatened-count').textContent = data.threatened_species || '4';
    document.getElementById('commercial-count').textContent = data.commercial_species || '7';
    
    document.getElementById('avg-temp').textContent = (data.avg_temperature || 27.8) + '°C';
    document.getElementById('avg-ph').textContent = data.avg_ph || '8.09';
    document.getElementById('avg-salinity').textContent = (data.avg_salinity || 34.9) + ' PSU';
    document.getElementById('avg-oxygen').textContent = (data.avg_oxygen || 5.7) + ' ml/L';
    
    document.getElementById('total-detected').textContent = data.total_species_detected || '1,127';
    document.getElementById('avg-reads').textContent = data.avg_reads || '48,234';
}

// Initialize interactive map
function initializeMap() {
    // Initialize Leaflet map
    researchMap = L.map('research-map').setView([12.0, 77.0], 6);
    
    // Add base layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(researchMap);
    
    // Load map data
    loadMapData('species');
    
    // Setup map layer control
    document.getElementById('map-layer-select').addEventListener('change', function(e) {
        loadMapData(e.target.value);
    });
}

function loadMapData(layer) {
    // Clear existing markers
    researchMap.eachLayer(function(layer) {
        if (layer instanceof L.Marker || layer instanceof L.CircleMarker) {
            researchMap.removeLayer(layer);
        }
    });
    
    // Load data based on selected layer
    switch(layer) {
        case 'species':
            loadSpeciesDistribution();
            break;
        case 'ocean':
            loadOceanParameters();
            break;
        case 'edna':
            loadEdnaSites();
            break;
        case 'routes':
            loadMaritimeRoutes();
            break;
    }
}

function loadSpeciesDistribution() {
    // Mock species distribution data
    const speciesData = [
        {lat: 15.123, lng: 73.543, species: 'Yellowfin Tuna', count: 45, status: 'Near Threatened'},
        {lat: 9.933, lng: 76.266, species: 'Indian Oil Sardine', count: 120, status: 'Least Concern'},
        {lat: 11.456, lng: 75.234, species: 'Red Snapper', count: 23, status: 'Vulnerable'},
        {lat: 13.789, lng: 80.123, species: 'Dusky Grouper', count: 8, status: 'Endangered'},
        {lat: 8.567, lng: 77.891, species: 'Indian Mackerel', count: 89, status: 'Least Concern'}
    ];
    
    speciesData.forEach(function(point) {
        const color = getStatusColor(point.status);
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: Math.sqrt(point.count) * 2,
            fillColor: color,
            color: color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.6
        }).addTo(researchMap);
        
        marker.bindPopup(`
            <strong>${point.species}</strong><br>
            Count: ${point.count}<br>
            Status: ${point.status}
        `);
    });
}

function loadOceanParameters() {
    // Mock ocean data
    const oceanData = [
        {lat: 15.123, lng: 73.543, temp: 28.1, ph: 8.16, location: 'Mumbai Coastal Waters'},
        {lat: 9.933, lng: 76.266, temp: 29.3, ph: 8.05, location: 'Kochi Backwaters'},
        {lat: 11.456, lng: 75.234, temp: 27.8, ph: 8.12, location: 'Mangalore Coast'},
        {lat: 13.789, lng: 80.123, temp: 30.1, ph: 7.98, location: 'Chennai Nearshore'},
        {lat: 8.567, lng: 77.891, temp: 26.9, ph: 8.18, location: 'Trivandrum Deep Waters'}
    ];
    
    oceanData.forEach(function(point) {
        const color = getTemperatureColor(point.temp);
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: 8,
            fillColor: color,
            color: color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.6
        }).addTo(researchMap);
        
        marker.bindPopup(`
            <strong>${point.location}</strong><br>
            Temperature: ${point.temp}°C<br>
            pH: ${point.ph}
        `);
    });
}

function loadEdnaSites() {
    // Mock eDNA data
    const ednaData = [
        {lat: 15.12, lng: 73.54, sampleId: 'EDNA-IOD-001', species: 67, diversity: 2.45},
        {lat: 9.93, lng: 76.27, sampleId: 'EDNA-IOD-002', species: 89, diversity: 2.78},
        {lat: 11.46, lng: 75.23, sampleId: 'EDNA-IOD-003', species: 54, diversity: 2.12},
        {lat: 13.79, lng: 80.12, sampleId: 'EDNA-IOD-004', species: 103, diversity: 3.21},
        {lat: 8.57, lng: 77.89, sampleId: 'EDNA-IOD-005', species: 72, diversity: 2.56}
    ];
    
    ednaData.forEach(function(point) {
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: point.diversity * 3,
            fillColor: '#9b59b6',
            color: '#8e44ad',
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.6
        }).addTo(researchMap);
        
        marker.bindPopup(`
            <strong>${point.sampleId}</strong><br>
            Species Detected: ${point.species}<br>
            Shannon Diversity: ${point.diversity}
        `);
    });
}

function loadMaritimeRoutes() {
    // Mock maritime routes
    const routes = [
        {
            name: 'Mumbai-Kochi Commercial Route',
            coordinates: [[19.0760, 72.8777], [15.123, 73.543], [11.456, 75.234], [9.9312, 76.2673]],
            type: 'Commercial',
            traffic: 'High'
        },
        {
            name: 'Chennai-Visakhapatnam Fishing Route',
            coordinates: [[13.0827, 80.2707], [13.789, 80.123], [14.5, 80.8], [17.6868, 83.2185]],
            type: 'Fishing',
            traffic: 'Medium'
        }
    ];
    
    routes.forEach(function(route) {
        const color = route.type === 'Commercial' ? '#e74c3c' : '#3498db';
        const polyline = L.polyline(route.coordinates, {
            color: color,
            weight: 4,
            opacity: 0.7
        }).addTo(researchMap);
        
        polyline.bindPopup(`
            <strong>${route.name}</strong><br>
            Type: ${route.type}<br>
            Traffic: ${route.traffic}
        `);
    });
}

// Initialize charts
function initializeCharts() {
    initializeSpeciesChart();
    initializeOceanChart();
    initializeEdnaChart();
}

function initializeSpeciesChart() {
    const ctx = document.getElementById('species-chart').getContext('2d');
    speciesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Least Concern', 'Near Threatened', 'Vulnerable', 'Endangered', 'Critically Endangered'],
            datasets: [{
                data: [4, 2, 2, 1, 1],
                backgroundColor: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#8e44ad'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function initializeOceanChart() {
    const ctx = document.getElementById('ocean-chart').getContext('2d');
    oceanChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mumbai', 'Kochi', 'Mangalore', 'Chennai', 'Trivandrum'],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [28.1, 29.3, 27.8, 30.1, 26.9],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'pH Level',
                    data: [8.16, 8.05, 8.12, 7.98, 8.18],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function initializeEdnaChart() {
    const ctx = document.getElementById('edna-chart').getContext('2d');
    ednaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['EDNA-001', 'EDNA-002', 'EDNA-003', 'EDNA-004', 'EDNA-005'],
            datasets: [{
                label: 'Species Detected',
                data: [67, 89, 54, 103, 72],
                backgroundColor: '#9b59b6',
                borderColor: '#8e44ad',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load recent data table
function loadRecentData() {
    const mockData = [
        {type: 'Species', location: 'Mumbai Coast', date: '2024-08-28', quality: 'High', action: 'View'},
        {type: 'Ocean', location: 'Kochi Waters', date: '2024-08-27', quality: 'Good', action: 'View'},
        {type: 'eDNA', location: 'Chennai Shore', date: '2024-08-26', quality: 'High', action: 'View'},
        {type: 'Species', location: 'Goa Offshore', date: '2024-08-25', quality: 'Medium', action: 'View'},
        {type: 'Ocean', location: 'Mangalore Deep', date: '2024-08-24', quality: 'Good', action: 'View'}
    ];
    
    const tableBody = document.getElementById('recent-data-table');
    tableBody.innerHTML = mockData.map(row => `
        <tr>
            <td><span class="data-type ${row.type.toLowerCase()}">${row.type}</span></td>
            <td>${row.location}</td>
            <td>${row.date}</td>
            <td><span class="quality-badge ${row.quality.toLowerCase()}">${row.quality}</span></td>
            <td><button class="view-btn" onclick="viewDataDetail('${row.type}', '${row.location}')">View</button></td>
        </tr>
    `).join('');
}

// Event listeners
function setupEventListeners() {
    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // Click outside modal to close
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Tool functions
function openSpeciesIdentifier() {
    document.getElementById('species-modal').style.display = 'block';
    
    // Setup file upload
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('species-image');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#fdf2f2';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processSpeciesImage(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            processSpeciesImage(e.target.files[0]);
        }
    });
}

function processSpeciesImage(file) {
    const resultsDiv = document.getElementById('identification-results');
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Analyzing image...</p>
        </div>
    `;
    
    // Simulate AI processing
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <div class="identification-result">
                <h3>Identification Results</h3>
                <div class="result-item">
                    <h4>Yellowfin Tuna (Thunnus albacares)</h4>
                    <p><strong>Confidence:</strong> 87%</p>
                    <p><strong>Family:</strong> Scombridae</p>
                    <p><strong>Conservation Status:</strong> Near Threatened</p>
                    <p><strong>Commercial Importance:</strong> High</p>
                </div>
                <div class="result-item secondary">
                    <h4>Skipjack Tuna (Katsuwonus pelamis)</h4>
                    <p><strong>Confidence:</strong> 23%</p>
                    <p><strong>Family:</strong> Scombridae</p>
                </div>
            </div>
        `;
    }, 3000);
}

function openDataExport() {
    alert('Data export functionality would be implemented here. Users can export filtered datasets in various formats (CSV, JSON, Excel).');
}

function openCorrelationAnalysis() {
    alert('Correlation analysis tool would open here, showing relationships between ocean parameters and species distribution.');
}

function openSequenceAnalysis() {
    alert('DNA sequence analysis tool would open here for processing eDNA data and species identification.');
}

function viewDataDetail(type, location) {
    alert(`Viewing detailed ${type} data for ${location}. This would open a detailed view with all measurements and metadata.`);
}

// Utility functions
function getStatusColor(status) {
    const colors = {
        'Least Concern': '#27ae60',
        'Near Threatened': '#f39c12',
        'Vulnerable': '#e67e22',
        'Endangered': '#e74c3c',
        'Critically Endangered': '#8e44ad'
    };
    return colors[status] || '#95a5a6';
}

function getTemperatureColor(temp) {
    if (temp < 25) return '#3498db';
    if (temp < 28) return '#27ae60';
    if (temp < 30) return '#f39c12';
    return '#e74c3c';
}

function getMockResearcherData() {
    return {
        species_count: 10,
        ocean_datapoints: 15,
        edna_samples: 15,
        avg_diversity: 2.67,
        threatened_species: 4,
        commercial_species: 7,
        avg_temperature: 27.8,
        avg_ph: 8.09,
        avg_salinity: 34.9,
        avg_oxygen: 5.7,
        total_species_detected: 1127,
        avg_reads: 48234
    };
}

// Add CSS for dynamic elements
const style = document.createElement('style');
style.textContent = `
    .data-type {
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        color: white;
    }
    .data-type.species { background: #3498db; }
    .data-type.ocean { background: #1abc9c; }
    .data-type.edna { background: #9b59b6; }
    
    .quality-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .quality-badge.high { background: #27ae60; color: white; }
    .quality-badge.good { background: #f39c12; color: white; }
    .quality-badge.medium { background: #e67e22; color: white; }
    
    .view-btn {
        padding: 0.25rem 0.75rem;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
    }
    .view-btn:hover { background: #2980b9; }
    
    .identification-result {
        margin-top: 1rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .result-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 6px;
        border-left: 4px solid #3498db;
    }
    .result-item.secondary {
        border-left-color: #95a5a6;
        opacity: 0.8;
    }
    .result-item h4 {
        margin: 0 0 0.5rem 0;
        color: #2c3e50;
    }
    .result-item p {
        margin: 0.25rem 0;
        color: #7f8c8d;
    }
`;
document.head.appendChild(style);