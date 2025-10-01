// Main JavaScript for FishNet Platform
class FishNetAPI {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.cache = new Map();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadHeroStats();
    }

    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async loadHeroStats() {
        try {
            const [speciesCount, datasetCount, oceanDataCount] = await Promise.all([
                this.request('/species/count'),
                this.request('/datasets/count'),
                this.request('/ocean/datapoints/count')
            ]);

            this.updateStatCard('total-species', speciesCount.count);
            this.updateStatCard('total-datasets', datasetCount.count);
            this.updateStatCard('ocean-datapoints', this.formatNumber(oceanDataCount.count));
        } catch (error) {
            console.error('Failed to load hero stats:', error);
        }
    }

    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M+';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K+';
        }
        return num.toLocaleString();
    }

    setupEventListeners() {
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        this.setupFormHandlers();
    }

    setupFormHandlers() {
        const speciesSearchForm = document.getElementById('species-search-form');
        if (speciesSearchForm) {
            speciesSearchForm.addEventListener('submit', this.handleSpeciesSearch.bind(this));
        }

        const speciesIdentificationForm = document.getElementById('species-identification-form');
        if (speciesIdentificationForm) {
            speciesIdentificationForm.addEventListener('submit', this.handleSpeciesIdentification.bind(this));
        }

        const uploadForm = document.getElementById('upload-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', this.handleDatasetUpload.bind(this));
        }
    }

    async handleSpeciesSearch(event) {
        event.preventDefault();
        const query = document.getElementById('species-search-input').value;
        if (!query.trim()) return;
        this.showLoading('species-results');
        try {
            const results = await this.request(`/species/search?q=${encodeURIComponent(query)}`);
            this.displaySpeciesResults(results.results);
        } catch (error) {
            this.showError('species-results', 'Failed to search species. Please try again.');
        }
    }

    displaySpeciesResults(results) {
        const container = document.getElementById('species-results');
        if (!results || results.length === 0) {
            container.innerHTML = '<p>No species found matching your search.</p>';
            return;
        }
        container.innerHTML = results.map(species => `
            <div class="search-result-item" onclick="viewSpeciesDetail(${species.id})">
                <div class="result-header">
                    <h4>${species.scientific_name}</h4>
                    ${species.common_name ? `<span class="common-name">${species.common_name}</span>` : ''}
                </div>
                <div class="result-details">
                    <span class="family">Family: ${species.family || 'Unknown'}</span>
                    <span class="status ${species.conservation_status ? species.conservation_status.toLowerCase().replace(' ', '-') : ''}">${species.conservation_status || 'Status Unknown'}</span>
                </div>
                ${species.habitat ? `<p class="habitat">Habitat: ${species.habitat}</p>` : ''}
            </div>
        `).join('');
    }

    async handleDatasetUpload(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const progressContainer = document.getElementById('upload-progress');
        const progressFill = progressContainer.querySelector('.progress-fill');
        const progressText = progressContainer.querySelector('.progress-text');
        
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Uploading dataset...';

        try {
            this.simulateProgress(progressFill, progressText);
            const response = await fetch('/api/datasets/upload', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Upload failed');
            const result = await response.json();
            progressFill.style.width = '100%';
            progressText.textContent = 'Upload completed successfully!';
            setTimeout(() => {
                progressContainer.style.display = 'none';
                this.closeDataUpload();
                this.showSuccess('Dataset uploaded and processed successfully!');
            }, 1500);
        } catch (error) {
            progressText.textContent = 'Upload failed. Please try again.';
            progressFill.style.backgroundColor = '#f44336';
            console.error('Upload error:', error);
        }
    }

    simulateProgress(progressFill, progressText) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                clearInterval(interval);
                return;
            }
            progressFill.style.width = `${progress}%`;
            if (progress < 30) {
                progressText.textContent = 'Uploading file...';
            } else if (progress < 60) {
                progressText.textContent = 'Processing data...';
            } else {
                progressText.textContent = 'Analyzing dataset...';
            }
        }, 200);
    }

    showLoading(containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading...</p></div>';
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i><p>${message}</p></div>`;
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.innerHTML = `<i class="fas fa-check-circle"></i><span>${message}</span>`;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    async handleSpeciesIdentification(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        this.showLoading('identification-results');
        try {
            const response = await fetch('/api/species/identify', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Identification failed');
            const results = await response.json();
            this.displayIdentificationResults(results.results);
        } catch (error) {
            this.showError('identification-results', 'Failed to identify species. Please try again.');
        }
    }

    displayIdentificationResults(results) {
        const container = document.getElementById('identification-results');
        if (!results || results.length === 0) {
            container.innerHTML = '<p>Could not identify the species from the image.</p>';
            return;
        }
        container.innerHTML = results.map(species => `
            <div class="search-result-item" onclick="viewSpeciesDetail(${species.id})">
                <div class="result-header">
                    <h4>${species.scientific_name}</h4>
                    <span class="common-name">${species.common_name}</span>
                </div>
                <div class="result-details">
                    <span class="family">Family: ${species.family}</span>
                    <span class="status ${species.conservation_status.toLowerCase().replace(' ', '-')}">${species.conservation_status}</span>
                </div>
                <p class="habitat">Habitat: ${species.habitat}</p>
            </div>
        `).join('');
    }
}

// Modal Management
function openSpeciesSearch() { document.getElementById('species-search-modal').style.display = 'block'; }
function closeSpeciesSearch() { document.getElementById('species-search-modal').style.display = 'none'; }
function openSpeciesIdentification() { document.getElementById('species-identification-modal').style.display = 'block'; }
function closeSpeciesIdentification() { document.getElementById('species-identification-modal').style.display = 'none'; }
function openDataUpload() { document.getElementById('data-upload-modal').style.display = 'block'; }
function closeDataUpload() {
    const modal = document.getElementById('data-upload-modal');
    modal.style.display = 'none';
    const form = document.getElementById('upload-form');
    if (form) form.reset();
    const progress = document.getElementById('upload-progress');
    if (progress) progress.style.display = 'none';
}

async function viewSpeciesDetail(speciesId) {
    const modal = document.getElementById('species-modal');
    const modalContent = document.getElementById('species-modal-content');
    modalContent.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading species details...</p></div>';
    modal.style.display = 'block';
    try {
        const species = await window.fishNetAPI.request(`/species/${speciesId}`);
        modalContent.innerHTML = `
            <div class="species-detail-header">
                <h2>${species.scientific_name}</h2>
                ${species.common_name ? `<h3>(${species.common_name})</h3>` : ''}
            </div>
            <div class="species-detail-body">
                <div class="species-image-container">
                    <img src="${species.image_url}" alt="${species.scientific_name}" onerror="this.onerror=null;this.src='/static/images/species/default.jpg';"/>
                </div>
                <div class="species-info">
                    <p><strong>Family:</strong> ${species.family || 'N/A'}</p>
                    <p><strong>Habitat:</strong> ${species.habitat || 'N/A'}</p>
                    <p><strong>Conservation Status:</strong> <span class="status ${species.conservation_status ? species.conservation_status.toLowerCase().replace(' ', '-') : ''}">${species.conservation_status || 'N/A'}</span></p>
                </div>
            </div>`;
    } catch (error) {
        console.error('Failed to load species details:', error);
        modalContent.innerHTML = '<div class="error-message"><i class="fas fa-exclamation-triangle"></i><p>Failed to load species details.</p></div>';
    }
}

function searchSpecies() {
    const form = document.getElementById('species-search-form');
    if (form) form.dispatchEvent(new Event('submit'));
}

window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

const speciesModal = document.getElementById('species-modal');
const closeSpeciesModalButton = speciesModal ? speciesModal.querySelector('.close-button') : null;
if (closeSpeciesModalButton) {
    closeSpeciesModalButton.addEventListener('click', () => {
        speciesModal.style.display = 'none';
    });
}

// --- App Initialization & Immersive Transitions ---
document.addEventListener('DOMContentLoaded', () => {
    if (window.__fishnetAppInitialized) return;
    window.__fishnetAppInitialized = true;

    window.fishNetAPI = new FishNetAPI();

    function createBackgroundEffects() {
        if (document.querySelector('.background-effects')) return;
        const effectsContainer = document.createElement('div');
        effectsContainer.className = 'background-effects';
        const caustics = document.createElement('div');
        caustics.className = 'caustics';
        effectsContainer.appendChild(caustics);
        const bubbles = document.createElement('div');
        bubbles.className = 'bubbles';
        for (let i = 0; i < 20; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            const size = Math.random() * 20 + 5;
            bubble.style.width = `${size}px`;
            bubble.style.height = `${size}px`;
            bubble.style.left = `${Math.random() * 100}%`;
            bubble.style.animationDuration = `${Math.random() * 15 + 10}s`;
            bubble.style.animationDelay = `${Math.random() * 10}s`;
            bubbles.appendChild(bubble);
        }
        effectsContainer.appendChild(bubbles);
        document.body.prepend(effectsContainer);
    }

    function immersiveNavigate(href) {
        if (window.__isNavigating) return;
        window.__isNavigating = true;

        const overlay = document.createElement('div');
        overlay.className = 'transition-overlay';
        const sonar = document.createElement('div');
        sonar.className = 'sonar-sweep';
        overlay.appendChild(sonar);
        document.body.appendChild(overlay);

        requestAnimationFrame(() => {
            overlay.classList.add('is-active');
        });

        setTimeout(() => {
            window.location.href = href;
        }, 800);

        setTimeout(() => {
            window.__isNavigating = false;
        }, 1200);
    }

    createBackgroundEffects();

    document.body.classList.add('page-enter-pro');
    setTimeout(() => {
        document.body.classList.remove('page-enter-pro');
    }, 1000);

    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href]');
        if (!link || link.target === '_blank' || link.hasAttribute('download') || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
            return;
        }
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#')) {
            return;
        }
        const url = new URL(link.href, window.location.href);
        if (url.origin !== window.location.origin) {
            return;
        }
        e.preventDefault();
        immersiveNavigate(link.href);
    });
});
