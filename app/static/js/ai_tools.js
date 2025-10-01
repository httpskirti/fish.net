// AI Tools JavaScript Functions

// Initialize AI Tools page
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Tools page loaded');
    initializeAITools();
});

function initializeAITools() {
    // Add any initialization code here
    console.log('AI Tools initialized');
}

// Species Identification Tool
function openSpeciesIdentification() {
    const modal = createModal('Species Identification', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-camera"></i> Upload Fish Image</h3>
            <p>Upload an image of a fish for automatic species identification using AI.</p>
            
            <div class="form-group">
                <label for="species-image">Select Image:</label>
                <input type="file" id="species-image" accept="image/*" onchange="previewImage(this)">
                <small>Supported formats: JPG, PNG, GIF (Max 10MB)</small>
            </div>
            
            <div id="image-preview" class="image-preview" style="display: none;">
                <img id="preview-img" src="" alt="Preview">
            </div>
            
            <div class="form-group">
                <label for="confidence-threshold">Confidence Threshold:</label>
                <input type="range" id="confidence-threshold" min="0.1" max="1.0" step="0.1" value="0.7">
                <span id="confidence-value">70%</span>
            </div>
            
            <button class="btn btn-primary" onclick="identifySpecies()">
                <i class="fas fa-search"></i> Identify Species
            </button>
            
            <div id="identification-results" class="results-container" style="display: none;">
                <!-- Results will be displayed here -->
            </div>
        </div>
    `);
    
    // Update confidence display
    const slider = modal.querySelector('#confidence-threshold');
    const display = modal.querySelector('#confidence-value');
    slider.addEventListener('input', function() {
        display.textContent = Math.round(this.value * 100) + '%';
    });
}

// Population Analysis Tool
function openPopulationAnalysis() {
    const modal = createModal('Population Analysis', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-chart-line"></i> Species Population Analysis</h3>
            <p>Analyze population trends and predict future changes for marine species.</p>
            
            <div class="form-group">
                <label for="analysis-species">Select Species:</label>
                <select id="analysis-species">
                    <option value="">Choose a species...</option>
                    <option value="tuna">Bluefin Tuna</option>
                    <option value="shark">Great White Shark</option>
                    <option value="dolphin">Bottlenose Dolphin</option>
                    <option value="whale">Humpback Whale</option>
                    <option value="custom">Custom Species</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="analysis-region">Region:</label>
                <select id="analysis-region">
                    <option value="indian-ocean">Indian Ocean</option>
                    <option value="arabian-sea">Arabian Sea</option>
                    <option value="bay-of-bengal">Bay of Bengal</option>
                    <option value="global">Global</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="time-range">Time Range:</label>
                <select id="time-range">
                    <option value="5">Last 5 years</option>
                    <option value="10">Last 10 years</option>
                    <option value="20">Last 20 years</option>
                    <option value="all">All available data</option>
                </select>
            </div>
            
            <button class="btn btn-primary" onclick="runPopulationAnalysis()">
                <i class="fas fa-play"></i> Run Analysis
            </button>
            
            <div id="analysis-results" class="results-container" style="display: none;">
                <!-- Analysis results will be displayed here -->
            </div>
        </div>
    `);
}

// Ocean Health Predictor
function openOceanPredictor() {
    const modal = createModal('Ocean Health Predictor', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-water"></i> Ocean Health Assessment</h3>
            <p>Predict ocean health based on environmental parameters and trends.</p>
            
            <div class="form-group">
                <label for="temperature">Water Temperature (°C):</label>
                <input type="number" id="temperature" min="0" max="40" step="0.1" placeholder="e.g., 25.5">
            </div>
            
            <div class="form-group">
                <label for="salinity">Salinity (PSU):</label>
                <input type="number" id="salinity" min="0" max="50" step="0.1" placeholder="e.g., 35.0">
            </div>
            
            <div class="form-group">
                <label for="ph-level">pH Level:</label>
                <input type="number" id="ph-level" min="6" max="9" step="0.1" placeholder="e.g., 8.1">
            </div>
            
            <div class="form-group">
                <label for="oxygen-level">Dissolved Oxygen (mg/L):</label>
                <input type="number" id="oxygen-level" min="0" max="15" step="0.1" placeholder="e.g., 7.5">
            </div>
            
            <div class="form-group">
                <label for="chlorophyll">Chlorophyll-a (μg/L):</label>
                <input type="number" id="chlorophyll" min="0" max="100" step="0.1" placeholder="e.g., 2.5">
            </div>
            
            <button class="btn btn-primary" onclick="predictOceanHealth()">
                <i class="fas fa-cogs"></i> Predict Health
            </button>
            
            <div id="prediction-results" class="results-container" style="display: none;">
                <!-- Prediction results will be displayed here -->
            </div>
        </div>
    `);
}

// eDNA Analyzer
function openEdnaAnalyzer() {
    const modal = createModal('eDNA Analyzer', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-dna"></i> Environmental DNA Analysis</h3>
            <p>Process eDNA sequences to identify species and assess biodiversity.</p>
            
            <div class="form-group">
                <label for="edna-file">Upload eDNA Sequence File:</label>
                <input type="file" id="edna-file" accept=".fasta,.fastq,.txt">
                <small>Supported formats: FASTA, FASTQ, TXT</small>
            </div>
            
            <div class="form-group">
                <label for="sequence-type">Sequence Type:</label>
                <select id="sequence-type">
                    <option value="16s">16S rRNA</option>
                    <option value="18s">18S rRNA</option>
                    <option value="coi">COI (Cytochrome Oxidase I)</option>
                    <option value="its">ITS (Internal Transcribed Spacer)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="similarity-threshold">Similarity Threshold:</label>
                <input type="range" id="similarity-threshold" min="0.8" max="1.0" step="0.01" value="0.97">
                <span id="similarity-value">97%</span>
            </div>
            
            <button class="btn btn-primary" onclick="analyzeEdna()">
                <i class="fas fa-microscope"></i> Analyze eDNA
            </button>
            
            <div id="edna-results" class="results-container" style="display: none;">
                <!-- eDNA analysis results will be displayed here -->
            </div>
        </div>
    `);
    
    // Update similarity display
    const slider = modal.querySelector('#similarity-threshold');
    const display = modal.querySelector('#similarity-value');
    slider.addEventListener('input', function() {
        display.textContent = Math.round(this.value * 100) + '%';
    });
}

// Threat Assessment
function openThreatAssessment() {
    const modal = createModal('Threat Assessment', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-exclamation-triangle"></i> Environmental Threat Assessment</h3>
            <p>AI-powered assessment of environmental threats to marine ecosystems.</p>
            
            <div class="form-group">
                <label for="threat-location">Location:</label>
                <input type="text" id="threat-location" placeholder="e.g., Arabian Sea, coordinates">
            </div>
            
            <div class="form-group">
                <label for="threat-types">Threat Types:</label>
                <div class="checkbox-group">
                    <label><input type="checkbox" value="pollution"> Pollution</label>
                    <label><input type="checkbox" value="overfishing"> Overfishing</label>
                    <label><input type="checkbox" value="climate-change"> Climate Change</label>
                    <label><input type="checkbox" value="habitat-loss"> Habitat Loss</label>
                    <label><input type="checkbox" value="invasive-species"> Invasive Species</label>
                </div>
            </div>
            
            <div class="form-group">
                <label for="assessment-period">Assessment Period:</label>
                <select id="assessment-period">
                    <option value="current">Current Status</option>
                    <option value="5-year">5-Year Projection</option>
                    <option value="10-year">10-Year Projection</option>
                    <option value="20-year">20-Year Projection</option>
                </select>
            </div>
            
            <button class="btn btn-primary" onclick="assessThreats()">
                <i class="fas fa-shield-alt"></i> Assess Threats
            </button>
            
            <div id="threat-results" class="results-container" style="display: none;">
                <!-- Threat assessment results will be displayed here -->
            </div>
        </div>
    `);
}

// Habitat Mapping
function openHabitatMapping() {
    const modal = createModal('Habitat Mapping', `
        <div class="ai-tool-content">
            <h3><i class="fas fa-map-marked-alt"></i> Habitat Suitability Mapping</h3>
            <p>Generate habitat suitability maps for marine species using AI models.</p>
            
            <div class="form-group">
                <label for="target-species">Target Species:</label>
                <input type="text" id="target-species" placeholder="e.g., Bluefin Tuna">
            </div>
            
            <div class="form-group">
                <label for="map-region">Map Region:</label>
                <select id="map-region">
                    <option value="indian-ocean">Indian Ocean</option>
                    <option value="arabian-sea">Arabian Sea</option>
                    <option value="bay-of-bengal">Bay of Bengal</option>
                    <option value="custom">Custom Coordinates</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="environmental-factors">Environmental Factors:</label>
                <div class="checkbox-group">
                    <label><input type="checkbox" value="temperature" checked> Temperature</label>
                    <label><input type="checkbox" value="depth" checked> Depth</label>
                    <label><input type="checkbox" value="salinity" checked> Salinity</label>
                    <label><input type="checkbox" value="currents"> Ocean Currents</label>
                    <label><input type="checkbox" value="productivity"> Primary Productivity</label>
                </div>
            </div>
            
            <div class="form-group">
                <label for="resolution">Map Resolution:</label>
                <select id="resolution">
                    <option value="low">Low (Fast)</option>
                    <option value="medium">Medium (Balanced)</option>
                    <option value="high">High (Detailed)</option>
                </select>
            </div>
            
            <button class="btn btn-primary" onclick="generateHabitatMap()">
                <i class="fas fa-map"></i> Generate Map
            </button>
            
            <div id="mapping-results" class="results-container" style="display: none;">
                <!-- Habitat mapping results will be displayed here -->
            </div>
        </div>
    `);
}

// Utility Functions
function createModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeModal(this)">&times;</span>
            <h2>${title}</h2>
            ${content}
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'block';
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal(modal.querySelector('.close'));
        }
    });
    
    return modal;
}

function closeModal(closeBtn) {
    const modal = closeBtn.closest('.modal');
    modal.style.display = 'none';
    setTimeout(() => {
        document.body.removeChild(modal);
    }, 300);
}

function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            const img = document.getElementById('preview-img');
            img.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// AI Tool Functions (Mock implementations)
function identifySpecies() {
    const resultsDiv = document.getElementById('identification-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Analyzing image...</p>
        </div>
    `;
    
    // Simulate AI processing
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>Identification Results</h4>
            <div class="species-result">
                <h5>Bluefin Tuna (Thunnus thynnus)</h5>
                <p><strong>Confidence:</strong> 87%</p>
                <p><strong>Family:</strong> Scombridae</p>
                <p><strong>Conservation Status:</strong> Endangered</p>
            </div>
            <div class="species-result">
                <h5>Yellowfin Tuna (Thunnus albacares)</h5>
                <p><strong>Confidence:</strong> 23%</p>
                <p><strong>Family:</strong> Scombridae</p>
                <p><strong>Conservation Status:</strong> Near Threatened</p>
            </div>
        `;
    }, 3000);
}

function runPopulationAnalysis() {
    const resultsDiv = document.getElementById('analysis-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Running population analysis...</p>
        </div>
    `;
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>Population Analysis Results</h4>
            <div class="analysis-summary">
                <p><strong>Current Population Trend:</strong> Declining (-15% over 10 years)</p>
                <p><strong>Predicted 5-year Change:</strong> -8%</p>
                <p><strong>Risk Level:</strong> High</p>
                <p><strong>Key Factors:</strong> Overfishing, habitat loss, climate change</p>
            </div>
            <button class="btn btn-secondary" onclick="downloadAnalysisReport()">
                <i class="fas fa-download"></i> Download Report
            </button>
        `;
    }, 4000);
}

function predictOceanHealth() {
    const resultsDiv = document.getElementById('prediction-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Analyzing ocean parameters...</p>
        </div>
    `;
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>Ocean Health Prediction</h4>
            <div class="health-score">
                <h5>Overall Health Score: 72/100</h5>
                <div class="health-indicators">
                    <p><strong>Temperature:</strong> Normal range</p>
                    <p><strong>pH Level:</strong> Slightly acidic (concern)</p>
                    <p><strong>Oxygen:</strong> Good levels</p>
                    <p><strong>Productivity:</strong> Above average</p>
                </div>
                <div class="recommendations">
                    <h6>Recommendations:</h6>
                    <ul>
                        <li>Monitor pH levels closely</li>
                        <li>Reduce carbon emissions in the area</li>
                        <li>Continue current conservation efforts</li>
                    </ul>
                </div>
            </div>
        `;
    }, 3500);
}

function analyzeEdna() {
    const resultsDiv = document.getElementById('edna-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Processing eDNA sequences...</p>
        </div>
    `;
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>eDNA Analysis Results</h4>
            <div class="edna-summary">
                <p><strong>Total Sequences Processed:</strong> 1,247</p>
                <p><strong>Species Identified:</strong> 23</p>
                <p><strong>Biodiversity Index:</strong> 3.2 (High)</p>
            </div>
            <div class="species-list">
                <h6>Detected Species:</h6>
                <ul>
                    <li>Bluefin Tuna (98% similarity)</li>
                    <li>Great White Shark (95% similarity)</li>
                    <li>Bottlenose Dolphin (97% similarity)</li>
                    <li>Sea Turtle sp. (92% similarity)</li>
                    <li>+ 19 more species</li>
                </ul>
            </div>
        `;
    }, 5000);
}

function assessThreats() {
    const resultsDiv = document.getElementById('threat-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Assessing environmental threats...</p>
        </div>
    `;
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>Threat Assessment Results</h4>
            <div class="threat-levels">
                <div class="threat-item high">
                    <h6>Pollution - HIGH RISK</h6>
                    <p>Plastic debris and chemical runoff detected</p>
                </div>
                <div class="threat-item medium">
                    <h6>Overfishing - MEDIUM RISK</h6>
                    <p>Fishing pressure above sustainable levels</p>
                </div>
                <div class="threat-item low">
                    <h6>Climate Change - LOW RISK (current)</h6>
                    <p>Temperature changes within normal range</p>
                </div>
            </div>
            <div class="action-plan">
                <h6>Recommended Actions:</h6>
                <ol>
                    <li>Implement stricter pollution controls</li>
                    <li>Establish fishing quotas</li>
                    <li>Monitor temperature trends</li>
                </ol>
            </div>
        `;
    }, 4500);
}

function generateHabitatMap() {
    const resultsDiv = document.getElementById('mapping-results');
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Generating habitat suitability map...</p>
        </div>
    `;
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <h4>Habitat Mapping Results</h4>
            <div class="map-placeholder">
                <p><i class="fas fa-map"></i> Interactive habitat map would be displayed here</p>
                <p><strong>High Suitability Areas:</strong> 15% of region</p>
                <p><strong>Medium Suitability:</strong> 35% of region</p>
                <p><strong>Low Suitability:</strong> 50% of region</p>
            </div>
            <div class="map-controls">
                <button class="btn btn-secondary" onclick="downloadMap()">
                    <i class="fas fa-download"></i> Download Map
                </button>
                <button class="btn btn-outline" onclick="shareMap()">
                    <i class="fas fa-share"></i> Share Map
                </button>
            </div>
        `;
    }, 6000);
}

// Additional utility functions
function downloadAnalysisReport() {
    alert('Analysis report download would start here');
}

function downloadMap() {
    alert('Map download would start here');
}

function shareMap() {
    alert('Map sharing options would appear here');
}

// Add CSS for results styling
const style = document.createElement('style');
style.textContent = `
    .results-container {
        margin-top: 2rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
    
    .species-result, .analysis-summary, .health-score, .edna-summary {
        background: white;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .threat-item {
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 4px solid;
    }
    
    .threat-item.high { border-color: #e74c3c; background: #fdf2f2; }
    .threat-item.medium { border-color: #f39c12; background: #fef9e7; }
    .threat-item.low { border-color: #27ae60; background: #eafaf1; }
    
    .image-preview {
        text-align: center;
        margin: 1rem 0;
    }
    
    .image-preview img {
        max-width: 100%;
        max-height: 200px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .checkbox-group {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .checkbox-group label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: normal;
    }
    
    .map-placeholder {
        background: #ecf0f1;
        padding: 3rem;
        text-align: center;
        border-radius: 8px;
        margin: 1rem 0;
        color: #7f8c8d;
    }
    
    .map-controls {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1rem;
    }
`;
document.head.appendChild(style);