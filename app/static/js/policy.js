// Policy Dashboard JavaScript

let policyMap;
let trendsChart, conservationChart;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Policy Dashboard loaded');
    initializePolicyDashboard();
});

function initializePolicyDashboard() {
    loadDashboardData();
    initializeMap();
    initializeCharts();
    setupEventListeners();
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load summary statistics
        const response = await fetch('/api/data/policy/summary');
        if (response.ok) {
            const data = await response.json();
            updateStatistics(data);
        } else {
            // Use mock data for demo
            updateStatistics(getMockPolicyData());
        }
        
        // Load decision support cards
        loadDecisionCards();
        
        // Load risk zones
        loadRiskZones();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Use mock data as fallback
        updateStatistics(getMockPolicyData());
        loadDecisionCards();
        loadRiskZones();
    }
}

function updateStatistics(data) {
    document.getElementById('critical-species').textContent = data.critical_species || '2';
    document.getElementById('commercial-risk').textContent = data.commercial_risk || '3';
    document.getElementById('protected-areas').textContent = data.protected_areas || '5';
    document.getElementById('trend-positive').textContent = data.trend_positive || '4';
    
    document.getElementById('declining-species').textContent = data.declining_species || '3';
    document.getElementById('stable-species').textContent = data.stable_species || '5';
    document.getElementById('increasing-species').textContent = data.increasing_species || '2';
}

// Initialize conservation priority map
function initializeMap() {
    // Initialize Leaflet map
    policyMap = L.map('policy-map').setView([12.0, 77.0], 6);
    
    // Add base layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(policyMap);
    
    // Load conservation zones
    loadConservationZones();
}

function loadConservationZones() {
    // Mock conservation priority zones
    const zones = [
        {
            lat: 15.123, lng: 73.543, 
            name: 'Mumbai Coastal Zone',
            risk: 'critical',
            species: ['Yellowfin Tuna', 'Indian Oil Sardine'],
            threats: ['Overfishing', 'Pollution'],
            recommendation: 'Implement immediate fishing restrictions'
        },
        {
            lat: 13.789, lng: 80.123,
            name: 'Chennai Marine Sanctuary',
            risk: 'high',
            species: ['Dusky Grouper', 'Green Turtle'],
            threats: ['Habitat loss', 'Climate change'],
            recommendation: 'Expand protected area boundaries'
        },
        {
            lat: 9.933, lng: 76.266,
            name: 'Kochi Backwater System',
            risk: 'medium',
            species: ['Indian Mackerel', 'Skipjack Tuna'],
            threats: ['Coastal development'],
            recommendation: 'Monitor water quality regularly'
        },
        {
            lat: 11.456, lng: 75.234,
            name: 'Mangalore Conservation Area',
            risk: 'low',
            species: ['Red Snapper', 'Grey Reef Shark'],
            threats: ['Minor fishing pressure'],
            recommendation: 'Continue current protection measures'
        },
        {
            lat: 8.567, lng: 77.891,
            name: 'Trivandrum Marine Reserve',
            risk: 'medium',
            species: ['Common Sawfish', 'Kawakawa'],
            threats: ['Tourism impact'],
            recommendation: 'Regulate tourism activities'
        }
    ];
    
    zones.forEach(function(zone) {
        const color = getRiskColor(zone.risk);
        const marker = L.circleMarker([zone.lat, zone.lng], {
            radius: 15,
            fillColor: color,
            color: color,
            weight: 3,
            opacity: 0.8,
            fillOpacity: 0.6
        }).addTo(policyMap);
        
        marker.bindPopup(`
            <div class="zone-popup">
                <h4>${zone.name}</h4>
                <p><strong>Risk Level:</strong> <span class="risk-${zone.risk}">${zone.risk.toUpperCase()}</span></p>
                <p><strong>Key Species:</strong> ${zone.species.join(', ')}</p>
                <p><strong>Main Threats:</strong> ${zone.threats.join(', ')}</p>
                <p><strong>Recommendation:</strong> ${zone.recommendation}</p>
                <button onclick="viewZoneDetails('${zone.name}')" class="zone-btn">View Details</button>
            </div>
        `);
    });
}

// Load decision support cards
function loadDecisionCards() {
    const decisions = [
        {
            type: 'critical',
            icon: 'fas fa-exclamation-triangle',
            title: 'Immediate Action Required',
            message: 'Dusky Grouper population in Chennai waters has declined by 40% in the last 6 months.',
            action: 'Implement emergency fishing ban in Zone C-12'
        },
        {
            type: 'warning',
            icon: 'fas fa-fish',
            title: 'Commercial Species Alert',
            message: 'Yellowfin Tuna catch rates are below sustainable levels in Mumbai coastal waters.',
            action: 'Reduce fishing quotas by 25% for next quarter'
        },
        {
            type: 'success',
            icon: 'fas fa-chart-line',
            title: 'Conservation Success',
            message: 'Indian Mackerel population showing 15% recovery in Kochi backwaters.',
            action: 'Continue current protection measures'
        },
        {
            type: 'critical',
            icon: 'fas fa-thermometer-half',
            title: 'Ocean Temperature Alert',
            message: 'Water temperatures in Arabian Sea 2°C above normal, affecting coral reefs.',
            action: 'Activate climate adaptation protocols'
        },
        {
            type: 'warning',
            icon: 'fas fa-industry',
            title: 'Pollution Concern',
            message: 'Elevated nitrate levels detected near major shipping routes.',
            action: 'Investigate industrial discharge sources'
        }
    ];
    
    const container = document.getElementById('decision-cards');
    container.innerHTML = decisions.map(decision => `
        <div class="decision-card ${decision.type}">
            <h4><i class="${decision.icon}"></i> ${decision.title}</h4>
            <p>${decision.message}</p>
            <div class="action">${decision.action}</div>
        </div>
    `).join('');
}

// Load risk zones
function loadRiskZones() {
    const criticalZones = [
        {name: 'Mumbai Coastal Zone', risk: 'Overfishing + Pollution'},
        {name: 'Chennai Marine Area', risk: 'Habitat Destruction'}
    ];
    
    const highZones = [
        {name: 'Kochi Backwaters', risk: 'Development Pressure'},
        {name: 'Goa Offshore', risk: 'Tourism Impact'},
        {name: 'Mangalore Coast', risk: 'Industrial Runoff'}
    ];
    
    document.getElementById('critical-zones').textContent = criticalZones.length;
    document.getElementById('high-zones').textContent = highZones.length;
    
    document.getElementById('critical-zone-list').innerHTML = criticalZones.map(zone => `
        <div class="zone-item">
            <span class="zone-name">${zone.name}</span>
            <span class="zone-risk critical">Critical</span>
        </div>
        <div class="zone-detail">${zone.risk}</div>
    `).join('');
    
    document.getElementById('high-zone-list').innerHTML = highZones.map(zone => `
        <div class="zone-item">
            <span class="zone-name">${zone.name}</span>
            <span class="zone-risk high">High</span>
        </div>
        <div class="zone-detail">${zone.risk}</div>
    `).join('');
}

// Initialize charts
function initializeCharts() {
    initializeTrendsChart();
    initializeConservationChart();
}

function initializeTrendsChart() {
    const ctx = document.getElementById('trends-chart').getContext('2d');
    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
            datasets: [
                {
                    label: 'Declining Species',
                    data: [2, 2, 3, 3, 4, 3, 3, 3],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Stable Species',
                    data: [4, 4, 4, 5, 5, 5, 5, 5],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Recovering Species',
                    data: [1, 1, 2, 2, 2, 2, 3, 2],
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 6
                }
            }
        }
    });
}

function initializeConservationChart() {
    const ctx = document.getElementById('conservation-chart').getContext('2d');
    conservationChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Least Concern', 'Near Threatened', 'Vulnerable', 'Endangered', 'Critically Endangered'],
            datasets: [{
                data: [4, 2, 2, 1, 1],
                backgroundColor: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#8e44ad'],
                borderWidth: 3,
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

// Action functions
function viewCriticalSpecies() {
    const modal = document.getElementById('species-detail-modal');
    const content = document.getElementById('species-detail-content');
    
    content.innerHTML = `
        <div class="critical-species-list">
            <h3>Species Requiring Immediate Attention</h3>
            
            <div class="species-item critical">
                <div class="species-header">
                    <h4>Dusky Grouper (Epinephelus marginatus)</h4>
                    <span class="status-badge endangered">Endangered</span>
                </div>
                <div class="species-details">
                    <p><strong>Population Trend:</strong> Declining (-40% in 6 months)</p>
                    <p><strong>Main Threats:</strong> Overfishing, habitat destruction</p>
                    <p><strong>Location:</strong> Chennai Marine Area</p>
                    <p><strong>Recommended Action:</strong> Immediate fishing ban, habitat restoration</p>
                </div>
            </div>
            
            <div class="species-item critical">
                <div class="species-header">
                    <h4>Common Sawfish (Pristis pristis)</h4>
                    <span class="status-badge critically-endangered">Critically Endangered</span>
                </div>
                <div class="species-details">
                    <p><strong>Population Trend:</strong> Severely declining</p>
                    <p><strong>Main Threats:</strong> Habitat loss, fishing pressure</p>
                    <p><strong>Location:</strong> Multiple coastal areas</p>
                    <p><strong>Recommended Action:</strong> Complete protection, breeding programs</p>
                </div>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function generateReport() {
    document.getElementById('report-modal').style.display = 'block';
}

function downloadReport() {
    const reportType = document.getElementById('report-type').value;
    const reportPeriod = document.getElementById('report-period').value;
    
    // Simulate report generation
    alert(`Generating ${reportType} report for ${reportPeriod}. In a real implementation, this would generate and download a PDF report with current conservation status, risk assessments, and policy recommendations.`);
    
    document.getElementById('report-modal').style.display = 'none';
}

function createAlert() {
    alert('Alert creation system would open here. Policy makers can set up automated alerts for specific species, regions, or environmental parameters.');
}

function scheduleAssessment() {
    alert('Assessment scheduling system would open here. Users can schedule regular conservation assessments and monitoring activities.');
}

function viewRegulations() {
    alert('Regulations viewer would open here, showing current fishing quotas, protected areas, and conservation policies.');
}

function exportSummary() {
    alert('Summary export functionality would generate executive reports suitable for policy briefings and stakeholder meetings.');
}

function viewZoneDetails(zoneName) {
    alert(`Detailed view for ${zoneName} would open here, showing comprehensive data about species, threats, and conservation measures.`);
}

// Utility functions
function getRiskColor(risk) {
    const colors = {
        'critical': '#e74c3c',
        'high': '#f39c12',
        'medium': '#f1c40f',
        'low': '#27ae60'
    };
    return colors[risk] || '#95a5a6';
}

function getMockPolicyData() {
    return {
        critical_species: 2,
        commercial_risk: 3,
        protected_areas: 5,
        trend_positive: 4,
        declining_species: 3,
        stable_species: 5,
        increasing_species: 2
    };
}

// Add CSS for dynamic elements
const style = document.createElement('style');
style.textContent = `
    .zone-popup {
        min-width: 250px;
    }
    .zone-popup h4 {
        margin: 0 0 0.5rem 0;
        color: #2c3e50;
    }
    .zone-popup p {
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .risk-critical { color: #e74c3c; font-weight: bold; }
    .risk-high { color: #f39c12; font-weight: bold; }
    .risk-medium { color: #f1c40f; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    
    .zone-btn {
        background: #3498db;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 0.5rem;
        font-size: 0.8rem;
    }
    .zone-btn:hover { background: #2980b9; }
    
    .zone-detail {
        font-size: 0.8rem;
        color: #7f8c8d;
        margin-top: 0.25rem;
        padding-left: 0.5rem;
        border-left: 2px solid #ecf0f1;
    }
    
    .critical-species-list {
        max-height: 400px;
        overflow-y: auto;
    }
    
    .species-item {
        border: 1px solid #ecf0f1;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .species-item.critical {
        border-left: 4px solid #e74c3c;
    }
    
    .species-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .species-header h4 {
        margin: 0;
        color: #2c3e50;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        color: white;
    }
    
    .status-badge.endangered { background: #e74c3c; }
    .status-badge.critically-endangered { background: #8e44ad; }
    
    .species-details p {
        margin: 0.25rem 0;
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    
    .species-details strong {
        color: #2c3e50;
    }
`;
document.head.appendChild(style);