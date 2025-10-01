class SpeciesPage {
    constructor() {
        this.speciesListContainer = document.getElementById('species-list-container');
        this.modal = document.getElementById('species-modal');
        this.modalContent = document.getElementById('species-modal-content');
        this.closeButton = document.querySelector('.close-button');
        this.init();
    }

    init() {
        this.loadSpeciesList();
        this.closeButton.addEventListener('click', () => this.closeModal());
        window.addEventListener('click', (event) => {
            if (event.target == this.modal) {
                this.closeModal();
            }
        });
    }

    async loadSpeciesList() {
        try {
            const response = await fetch('/api/species/');
            const data = await response.json();
            this.renderSpeciesList(data.species);
        } catch (error) {
            console.error('Failed to load species list:', error);
            this.speciesListContainer.innerHTML = '<p>Error loading species list.</p>';
        }
    }

    renderSpeciesList(species) {
        let html = '<div class="species-grid">';
        for (const s of species) {
            html += `
                <div class="species-card" onclick="speciesPage.showSpeciesDetail(${s.id})">
                    <img src="${s.image_url}" alt="${s.common_name}" onerror="this.src='/static/images/species/placeholder.jpg'">
                    <div class="species-card-info">
                        <h3>${s.common_name}</h3>
                        <p>${s.scientific_name}</p>
                    </div>
                </div>
            `;
        }
        html += '</div>';
        this.speciesListContainer.innerHTML = html;
    }

    async showSpeciesDetail(speciesId) {
        try {
            const response = await fetch(`/api/species/${speciesId}`);
            const speciesData = await response.json();
            this.renderSpeciesDetail(speciesData);
            this.openModal();
        } catch (error) {
            console.error('Failed to load species details:', error);
            this.modalContent.innerHTML = '<p>Error loading species details.</p>';
            this.openModal();
        }
    }

    renderSpeciesDetail(data) {
        this.modalContent.innerHTML = `
            <div class="species-detail-header">
                <img src="${data.image_url}" alt="${data.common_name}" onerror="this.src='/static/images/species/placeholder.jpg'">
                <div class="species-detail-title">
                    <h2>${data.common_name}</h2>
                    <h1>${data.scientific_name}</h1>
                </div>
            </div>
            <div class="species-detail-body">
                <p><strong>Family:</strong> ${data.family}</p>
                <p><strong>Habitat:</strong> ${data.habitat}</p>
                <p><strong>Conservation Status:</strong> ${data.conservation_status}</p>
            </div>
        `;
    }

    openModal() {
        this.modal.style.display = 'block';
    }

    closeModal() {
        this.modal.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.speciesPage = new SpeciesPage();
});
