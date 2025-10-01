// Dashboard-specific JavaScript
class Dashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.setupEventListeners();
        this.initializeCharts();
        this.startAutoRefresh();
    }

    async loadDashboardData() {
        try {
            // Load main statistics
            await this.loadMainStats();
            
            // Load recent datasets
            await this.loadRecentDatasets();
            
            // Update decision cards
            await this.updateDecisionCards();
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    async loadMainStats() {
        try {
            const stats = await fetch('/api/dashboard/stats').then(r => r.json());
            
            document.getElementById('total-datasets').textContent = stats.total_datasets.toLocaleString();
            document.getElementById('tracked-species').textContent = stats.tracked_species.toLocaleString();
            document.getElementById('active-research').textContent = stats.active_research;
            document.getElementById('system-health').textContent = stats.system_health;
            
            document.getElementById('ocean-datapoints').textContent = this.formatNumber(stats.ocean_datapoints);
            document.getElementById('edna-sequences').textContent = stats.edna_sequences.toLocaleString();
            document.getElementById('otolith-images').textContent = stats.otolith_images.toLocaleString();
            document.getElementById('api-requests').textContent = stats.api_requests_24h.toLocaleString();
            
        } catch (error) {
            console.error('Failed to load main stats:', error);
        }
    }

    async loadRecentDatasets() {
        try {
            const datasets = await fetch('/api/datasets/?limit=10').then(r => r.json());
            
            const tbody = document.getElementById('datasets-tbody');
            tbody.innerHTML = datasets.datasets.map(dataset => `
                <tr>
                    <td>${dataset.id}</td>
                    <td><span class="dataset-type">${dataset.dataset_type}</span></td>
                    <td>${dataset.region || 'Global'}</td>
                    <td>${new Date(dataset.uploaded_at).toLocaleDateString()}</td>
                    <td>${dataset.records_count || 0}</td>
                    <td><span class="status-badge ${dataset.processed ? 'processed' : 'processing'}">${dataset.processed ? 'Processed' : 'Processing'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="viewDataset(${dataset.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="downloadDataset(${dataset.id})">
                            <i class="fas fa-download"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load recent datasets:', error);
        }
    }

    async updateDecisionCards() {
        try {
            const decisions = await fetch('/api/dashboard/decisions').then(r => r.json());
            
            const container = document.getElementById('decision-cards');
            container.innerHTML = decisions.map(decision => `
                <div class="decision-card ${decision.type}">
                    <div class="card-header">
                        <i class="${decision.icon}"></i>
                        <span>${decision.title}</span>
                    </div>
                    <div class="card-content">
                        <p>${decision.message}</p>
                    </div>
                    <div class="card-action">
                        <button class="btn btn-sm ${decision.action_class}" onclick="handleDecision('${decision.id}')">
                            ${decision.action_text}
                        </button>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load decision cards:', error);
        }
    }

    initializeCharts() {
        // Species Distribution Chart
        const speciesCtx = document.getElementById('fisheries-chart');
        if (speciesCtx) {
            this.loadSpeciesChart();
        }

        // Remove correlation chart - not needed for prototype
        const correlationCtx = document.getElementById('correlation-chart');
        if (correlationCtx) {
            correlationCtx.style.display = 'none';
            const parent = correlationCtx.closest('.chart-container');
            if (parent) parent.style.display = 'none';
        }
    }

    async loadSpeciesChart() {
        try {
            const response = await fetch('/api/species/list');
            const data = await response.json();
            
            // Group species by conservation status
            const statusCounts = {};
            data.species.forEach(species => {
                const status = species.conservation_status || 'Unknown';
                statusCounts[status] = (statusCounts[status] || 0) + 1;
            });

            const ctx = document.getElementById('fisheries-chart');
            // Register a subtle glow plugin once to enhance arc rendering
            if (!this._glowPluginRegistered && window.Chart) {
                const hudGlow = {
                    id: 'hudGlow',
                    beforeDatasetDraw(chart, args) {
                        const { ctx } = chart;
                        ctx.save();
                        ctx.shadowColor = 'rgba(0, 229, 255, 0.25)';
                        ctx.shadowBlur = 14;
                        ctx.shadowOffsetX = 0;
                        ctx.shadowOffsetY = 0;
                    },
                    afterDatasetDraw(chart) {
                        chart.ctx.restore();
                    }
                };
                Chart.register(hudGlow);
                this._glowPluginRegistered = true;
            }
            this.charts.species = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(statusCounts),
                    datasets: [{
                        data: Object.values(statusCounts),
                        backgroundColor: [
                            '#3498db',
                            '#e74c3c',
                            '#f39c12',
                            '#2ecc71',
                            '#9b59b6',
                            '#1abc9c'
                        ],
                        borderColor: 'rgba(255,255,255,0.06)',
                        borderWidth: 2,
                        hoverOffset: 10,
                        hoverBorderColor: 'rgba(255,255,255,0.9)',
                        hoverBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '58%',
                    animation: {
                        animateRotate: true,
                        animateScale: true,
                        duration: 900,
                        easing: 'easeOutQuart'
                    },
                    interaction: { mode: 'nearest', intersect: false },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#d8f6ff' }
                        },
                        title: {
                            display: true,
                            text: 'Species by Conservation Status',
                            color: '#e8fbff'
                        },
                        tooltip: {
                            backgroundColor: 'rgba(7,25,34,0.95)',
                            borderColor: 'rgba(0, 239, 255, 0.25)',
                            borderWidth: 1,
                            padding: 12,
                            titleColor: '#e8fbff',
                            bodyColor: '#d8f6ff'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to load species chart:', error);
        }
    }

    // Removed random correlation data generation

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.loadDashboardData();
        }

        // Dataset upload button
        const uploadBtn = document.querySelector('[onclick="openDataUpload()"]');
        if (uploadBtn) {
            uploadBtn.onclick = openDataUpload;
        }

        // Correlation parameter selector
        const correlationSelect = document.getElementById('correlation-parameter');
        if (correlationSelect) {
            correlationSelect.addEventListener('change', (e) => {
                this.updateCorrelationChart(e.target.value);
            });
        }

        // Dashboard upload form
        const dashboardForm = document.getElementById('dashboard-upload-form');
        if (dashboardForm) {
            dashboardForm.addEventListener('submit', this.handleDashboardUpload.bind(this));
        }
    }

    async handleDashboardUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const progressContainer = document.getElementById('dashboard-upload-progress');
        const progressFill = progressContainer.querySelector('.progress-fill');
        const progressText = progressContainer.querySelector('.progress-text');
        
        progressContainer.style.display = 'block';
        
        try {
            const response = await fetch('/api/datasets/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const result = await response.json();
            
            progressFill.style.width = '100%';
            progressText.textContent = 'Upload completed successfully!';
            
            setTimeout(() => {
                closeDataUpload();
                this.loadDashboardData(); // Refresh dashboard
            }, 1500);

        } catch (error) {
            progressText.textContent = 'Upload failed. Please try again.';
            console.error('Dashboard upload error:', error);
        }
    }

    // Removed correlation chart functionality - not needed for prototype

    startAutoRefresh() {
        // Refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadMainStats();
        }, 5 * 60 * 1000);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M+';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K+';
        }
        return num.toLocaleString();
    }
}

// Global functions for dashboard
function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.loadDashboardData();
    }
}

function refreshFisheriesData() {
    // Simulate data refresh
    console.log('Refreshing fisheries data...');
}

function exportDatasets() {
    window.open('/api/datasets/export', '_blank');
}

function viewDataset(id) {
    window.location.href = `/datasets/${id}`;
}

function downloadDataset(id) {
    window.open(`/api/datasets/${id}/download`, '_blank');
}

function handleDecision(decisionId) {
    console.log('Handling decision:', decisionId);
    // Implement decision handling logic
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});