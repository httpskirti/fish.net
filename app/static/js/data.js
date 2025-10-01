// Data Page JavaScript

let currentChart = null;
let currentPage = 1;
let currentDataset = null;

// Initialize data page
document.addEventListener('DOMContentLoaded', function() {
    initializeDataPage();
    loadDataChart();
});

function initializeDataPage() {
    console.log('Data page initialized');
    
    // Add event listeners for forms
    const uploadForm = document.getElementById('data-upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleDataUpload);
    }
    
    // Initialize tooltips or other interactive elements
    initializeInteractiveElements();
}

function initializeInteractiveElements() {
    // Add hover effects to dataset cards
    const datasetCards = document.querySelectorAll('.dataset-card');
    datasetCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Data upload functionality
function openDataUpload() {
    const modal = document.getElementById('data-upload-modal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeDataUpload() {
    const modal = document.getElementById('data-upload-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Reset form
        const form = document.getElementById('data-upload-form');
        if (form) {
            form.reset();
        }
        
        // Hide progress
        const progress = document.getElementById('data-upload-progress');
        if (progress) {
            progress.style.display = 'none';
        }
    }
}

function handleDataUpload(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const progressContainer = document.getElementById('data-upload-progress');
    const progressFill = progressContainer.querySelector('.progress-fill');
    const progressText = progressContainer.querySelector('.progress-text');
    
    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading and processing dataset...';
    
    // Simulate upload progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        progressFill.style.width = progress + '%';
        
        if (progress > 30 && progress < 60) {
            progressText.textContent = 'Processing dataset structure...';
        } else if (progress >= 60) {
            progressText.textContent = 'Integrating with database...';
        }
    }, 200);
    
    // Simulate successful upload after 3 seconds
    setTimeout(() => {
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Dataset uploaded successfully!';
        
        setTimeout(() => {
            closeDataUpload();
            showNotification('Dataset uploaded and processed successfully!', 'success');
            refreshDatasets();
        }, 1000);
    }, 3000);
}

// Dataset management functions
function refreshDatasets() {
    console.log('Refreshing datasets...');
    showNotification('Datasets refreshed', 'info');
    
    // Update dataset counts and statistics
    updateDatasetStatistics();
}

function updateDatasetStatistics() {
    // Update the overview cards with current data
    const totalRecords = document.querySelector('.stat-card .stat-number');
    if (totalRecords && totalRecords.textContent === '9,513') {
        // Simulate data update
        const newCount = 9513 + Math.floor(Math.random() * 100);
        totalRecords.textContent = newCount.toLocaleString();
    }
}

function viewDataset(datasetType) {
    currentDataset = datasetType;
    const modal = document.getElementById('dataset-viewer-modal');
    const title = document.getElementById('viewer-title');
    
    if (modal && title) {
        title.innerHTML = `<i class="fas fa-table"></i> ${getDatasetDisplayName(datasetType)} Dataset`;
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        loadDatasetData(datasetType);
    }
}

function getDatasetDisplayName(type) {
    const names = {
        'species': 'Species',
        'ocean': 'Ocean',
        'edna': 'eDNA'
    };
    return names[type] || type;
}

function loadDatasetData(datasetType) {
    const thead = document.getElementById('dataset-thead');
    const tbody = document.getElementById('dataset-tbody');
    
    if (!thead || !tbody) return;
    
    // Sample data structure based on dataset type
    let headers = [];
    let sampleData = [];
    
    switch (datasetType) {
        case 'species':
            headers = ['ID', 'Scientific Name', 'Common Name', 'Family', 'Location', 'Date'];
            sampleData = [
                ['SP001', 'Thunnus albacares', 'Yellowfin Tuna', 'Scombridae', 'Arabian Sea', '2024-01-15'],
                ['SP002', 'Katsuwonus pelamis', 'Skipjack Tuna', 'Scombridae', 'Bay of Bengal', '2024-01-14'],
                ['SP003', 'Coryphaena hippurus', 'Mahi-mahi', 'Coryphaenidae', 'Indian Ocean', '2024-01-13'],
                ['SP004', 'Scomberomorus commerson', 'Spanish Mackerel', 'Scombridae', 'Arabian Sea', '2024-01-12'],
                ['SP005', 'Lutjanus campechanus', 'Red Snapper', 'Lutjanidae', 'Bay of Bengal', '2024-01-11']
            ];
            break;
        case 'ocean':
            headers = ['ID', 'Location', 'Temperature (°C)', 'Salinity (PSU)', 'pH', 'Date'];
            sampleData = [
                ['OC001', '15.5°N, 68.2°E', '28.5', '35.2', '8.1', '2024-01-15'],
                ['OC002', '12.3°N, 75.4°E', '29.1', '35.0', '8.0', '2024-01-14'],
                ['OC003', '18.7°N, 72.8°E', '27.8', '35.5', '8.2', '2024-01-13'],
                ['OC004', '20.1°N, 70.3°E', '28.9', '35.1', '8.1', '2024-01-12'],
                ['OC005', '14.2°N, 74.6°E', '29.3', '34.9', '7.9', '2024-01-11']
            ];
            break;
        case 'edna':
            headers = ['Sample ID', 'Location', 'Depth (m)', 'Species Detected', 'Confidence', 'Date'];
            sampleData = [
                ['ED001', '16.2°N, 69.1°E', '25', 'Thunnus albacares', '95%', '2024-01-15'],
                ['ED002', '13.5°N, 76.2°E', '30', 'Katsuwonus pelamis', '88%', '2024-01-14'],
                ['ED003', '19.1°N, 73.4°E', '15', 'Coryphaena hippurus', '92%', '2024-01-13'],
                ['ED004', '21.3°N, 71.7°E', '40', 'Scomberomorus commerson', '85%', '2024-01-12'],
                ['ED005', '15.8°N, 75.9°E', '20', 'Lutjanus campechanus', '90%', '2024-01-11']
            ];
            break;
    }
    
    // Populate headers
    thead.innerHTML = '<tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr>';
    
    // Populate data
    tbody.innerHTML = sampleData.map(row => 
        '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
    ).join('');
    
    // Update pagination
    document.getElementById('page-info').textContent = `Page 1 of 1 (${sampleData.length} records)`;
}

function closeDatasetViewer() {
    const modal = document.getElementById('dataset-viewer-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function searchDataset() {
    const searchTerm = document.getElementById('dataset-search').value.toLowerCase();
    const tbody = document.getElementById('dataset-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function downloadDataset(datasetType) {
    showNotification(`Downloading ${getDatasetDisplayName(datasetType)} dataset...`, 'info');
    
    // Simulate download
    setTimeout(() => {
        showNotification(`${getDatasetDisplayName(datasetType)} dataset downloaded successfully!`, 'success');
    }, 1500);
}

function exportAllData() {
    showNotification('Exporting all datasets...', 'info');
    
    // Simulate export
    setTimeout(() => {
        showNotification('All datasets exported successfully!', 'success');
    }, 2000);
}

function exportCurrentView() {
    showNotification('Exporting current view...', 'info');
    
    // Simulate export
    setTimeout(() => {
        showNotification('Current view exported successfully!', 'success');
    }, 1000);
}

// Chart functionality
function loadDataChart() {
    const ctx = document.getElementById('data-chart');
    if (!ctx) return;
    
    const chartData = {
        labels: ['Species Data', 'Ocean Data', 'eDNA Data'],
        datasets: [{
            label: 'Records Count',
            data: [2847, 5432, 1234],
            backgroundColor: [
                'rgba(255, 107, 107, 0.8)',
                'rgba(78, 205, 196, 0.8)',
                'rgba(69, 183, 209, 0.8)'
            ],
            borderColor: [
                'rgba(255, 107, 107, 1)',
                'rgba(78, 205, 196, 1)',
                'rgba(69, 183, 209, 1)'
            ],
            borderWidth: 2
        }]
    };
    
    currentChart = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: true,
                    text: 'Dataset Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#0d47a1'
                }
            }
        }
    });
}

function updateChart() {
    const chartType = document.getElementById('chart-type').value;
    
    if (!currentChart) return;
    
    let newData = {};
    
    switch (chartType) {
        case 'species-distribution':
            newData = {
                labels: ['Fish', 'Mammals', 'Invertebrates', 'Others'],
                datasets: [{
                    label: 'Species Count',
                    data: [1847, 234, 567, 199],
                    backgroundColor: [
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(78, 205, 196, 0.8)',
                        'rgba(69, 183, 209, 0.8)',
                        'rgba(249, 202, 36, 0.8)'
                    ]
                }]
            };
            break;
        case 'ocean-parameters':
            newData = {
                labels: ['Temperature', 'Salinity', 'pH', 'Oxygen', 'Turbidity'],
                datasets: [{
                    label: 'Measurements',
                    data: [1200, 1150, 980, 876, 654],
                    backgroundColor: [
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(78, 205, 196, 0.8)',
                        'rgba(69, 183, 209, 0.8)',
                        'rgba(249, 202, 36, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ]
                }]
            };
            break;
        case 'edna-diversity':
            newData = {
                labels: ['High Diversity', 'Medium Diversity', 'Low Diversity'],
                datasets: [{
                    label: 'Sample Count',
                    data: [456, 567, 211],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(244, 67, 54, 0.8)'
                    ]
                }]
            };
            break;
    }
    
    currentChart.data = newData;
    currentChart.update();
}

// Pagination functions
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadDatasetData(currentDataset);
    }
}

function nextPage() {
    // In a real implementation, you'd check if there are more pages
    currentPage++;
    loadDatasetData(currentDataset);
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
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
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
    }
});