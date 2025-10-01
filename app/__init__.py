from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api
import os
import csv
import json
from config import Config

# Import db from models
from app.models import db, SeaRoute

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Initialize Supabase client
    from supabase import create_client
    supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_ANON_KEY'])
    app.supabase = supabase
    
    # Configure static files properly
    app.static_folder = 'static'
    app.static_url_path = '/static'
    
    print("Flask app created, registering main routes...")
    
    # =============================================================================
    # MAIN WEBSITE ROUTES (Register BEFORE API to avoid conflicts)
    # =============================================================================
    
    @app.route('/')
    def index():
        """Homepage - FishNet Home"""
        print("Index route called!")
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"Error loading index template: {e}")
            return f'<h1>Home Page Error</h1><p>{e}</p><a href="/dashboard">Dashboard</a>'
    
    @app.route('/dashboard')
    def dashboard():
        """Main Dashboard"""
        print("Dashboard route called!")
        try:
            return render_template('dashboard.html')
        except Exception as e:
            return f'<h1>Dashboard Error</h1><p>{e}</p><a href="/">Home</a>'
    
    @app.route('/species')
    def species():
        """Species List Page - populated from sample CSV"""
        print("Species route called!")
        try:
            # Resolve sample CSV path
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            csv_path = os.path.join(root_dir, 'sample-species-data.csv')
            species_list = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    row['id'] = i + 1  # Add ID for linking
                    species_list.append(row)

            # Server-render clean, modern list using existing CSS
            html_items = []
            for s in species_list:
                # Check if species image exists
                image_filename = s.get('scientific_name', '').replace(' ', '_').lower() + '.jpg'
                image_path = f"/static/images/species/{image_filename}"
                
                # Check if image file exists
                full_image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'species', image_filename)
                image_exists = os.path.exists(full_image_path)
                
                if image_exists:
                    image_html = f'<img src="{image_path}" alt="{s.get("scientific_name", "")}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:1rem;">'
                else:
                    image_html = '''<div class="species-image" style="width:100%; height:150px; background: linear-gradient(135deg, #3498db, #2980b9); border-radius:8px; margin-bottom:1rem; display:flex; align-items:center; justify-content:center; color:white; font-size:2rem;">
                        <i class="fas fa-fish"></i>
                    </div>'''
                
                html_items.append(f'''
                    <div class="access-card species-card" style="text-align:left; cursor:pointer;" onclick="viewSpeciesDetail('{s.get('scientific_name', '')}')">
                        {image_html}
                        <h3 style="margin-bottom:0.25rem">{s.get('scientific_name','')}</h3>
                        <div class="text-secondary" style="margin-bottom:0.5rem">{s.get('common_name','')}</div>
                        <div class="text-secondary">Family: {s.get('family','')} | Status: {s.get('conservation_status','')}</div>
                        <div class="text-secondary">Habitat: {s.get('habitat','')}</div>
                    </div>
                ''')
            
            species_json = json.dumps(species_list)

            return f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Species - FishNet</title>
                <link rel="stylesheet" href="/static/css/style.css">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    .species-list-container {{ max-width: 1200px; margin: 120px auto 40px; padding: 0 1.5rem; }}
                    .species-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom: 1.5rem; }}
                    .species-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }}
                    .page-title {{ color: var(--heading-color); font-size: 1.75rem; }}
                    .subtitle {{ color: var(--text-color); }}
                    .species-card {{ transition: all 0.3s ease; }}
                    .species-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
                    
                    /* Species Detail Modal */
                    .species-modal {{ display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }}
                    .species-modal-content {{ background: white; margin: 2% auto; padding: 0; border-radius: 12px; width: 90%; max-width: 1000px; max-height: 90vh; overflow-y: auto; }}
                    .species-modal-header {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 2rem; border-radius: 12px 12px 0 0; }}
                    .species-modal-body {{ padding: 2rem; }}
                    .species-close {{ color: white; float: right; font-size: 2rem; cursor: pointer; }}
                    .species-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
                    .stat-box {{ background: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center; }}
                    .stat-value {{ font-size: 1.5rem; font-weight: bold; color: #3498db; }}
                    .stat-label {{ color: #6c757d; font-size: 0.9rem; }}
                    .chart-container {{ width: 100%; height: 300px; margin: 1rem 0; }}
                </style>
            </head>
            <body>
                <nav class="navbar">
                    <div class="nav-container">
                        <div class="nav-logo">
                            <a href="/" class="nav-logo-link"><h2><i class="fas fa-fish"></i> FishNet</h2></a>
                        </div>
                        <ul class="nav-menu">
                            <li><a href="/" class="nav-link">Home</a></li>
                            <li><a href="/dashboard" class="nav-link">Dashboard</a></li>
                            <li><a href="/species" class="nav-link active">Species</a></li>
                            <li><a href="/data" class="nav-link">Data</a></li>
                            <li><a href="/map" class="nav-link">Map</a></li>
                        </ul>
                    </div>
                </nav>

                <div class="species-list-container">
                    <div class="species-header">
                        <div>
                            <div class="page-title"><i class="fas fa-fish"></i> Species Database</div>
                            <div class="subtitle">Marine species from Indian Ocean dataset ({len(species_list)} records)</div>
                        </div>
                    </div>
                    <div class="species-grid">
                        {''.join(html_items)}
                    </div>
                </div>

                <!-- Species Detail Modal -->
                <div id="speciesModal" class="species-modal">
                    <div class="species-modal-content">
                        <div class="species-modal-header">
                            <span class="species-close" onclick="closeSpeciesModal()">&times;</span>
                            <div id="modalSpeciesName" style="font-size: 2rem; font-weight: bold;"></div>
                            <div id="modalCommonName" style="font-size: 1.2rem; opacity: 0.9;"></div>
                        </div>
                        <div class="species-modal-body">
                            <div id="modalSpeciesContent"></div>
                        </div>
                    </div>
                </div>

                <script>
                    const speciesData = {species_json};
                    
                    function viewSpeciesDetail(scientificName) {{
                        const species = speciesData.find(s => s.scientific_name === scientificName);
                        if (!species) return;
                        
                        document.getElementById('modalSpeciesName').textContent = species.scientific_name;
                        document.getElementById('modalCommonName').textContent = species.common_name || '';
                        
                        const content = `
                            <div class="species-stats">
                                <div class="stat-box">
                                    <div class="stat-value">${{species.max_length_cm || 'N/A'}}</div>
                                    <div class="stat-label">Max Length (cm)</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">${{species.trophic_level || 'N/A'}}</div>
                                    <div class="stat-label">Trophic Level</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">${{species.conservation_status || 'N/A'}}</div>
                                    <div class="stat-label">Conservation Status</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">${{species.commercial_importance || 'N/A'}}</div>
                                    <div class="stat-label">Commercial Value</div>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">
                                <div>
                                    <h3><i class="fas fa-info-circle"></i> Basic Information</h3>
                                    <p><strong>Family:</strong> ${{species.family || 'N/A'}}</p>
                                    <p><strong>Genus:</strong> ${{species.genus || 'N/A'}}</p>
                                    <p><strong>Order:</strong> ${{species.order || 'N/A'}}</p>
                                    <p><strong>Class:</strong> ${{species.class || 'N/A'}}</p>
                                    <p><strong>Habitat:</strong> ${{species.habitat || 'N/A'}}</p>
                                </div>
                                <div>
                                    <h3><i class="fas fa-thermometer-half"></i> Environmental Range</h3>
                                    <p><strong>Depth Range:</strong> ${{species.depth_min_m || 'N/A'}} - ${{species.depth_max_m || 'N/A'}} m</p>
                                    <p><strong>Temperature Range:</strong> ${{species.temperature_min_c || 'N/A'}} - ${{species.temperature_max_c || 'N/A'}} °C</p>
                                    <p><strong>Length Range:</strong> ${{species.min_length_cm || 'N/A'}} - ${{species.max_length_cm || 'N/A'}} cm</p>
                                </div>
                            </div>
                            
                            <div style="margin-top: 2rem;">
                                <h3><i class="fas fa-map-marker-alt"></i> Distribution</h3>
                                <p>${{species.distribution || 'Distribution information not available.'}}</p>
                            </div>
                            
                            <div style="margin-top: 2rem;">
                                <h3><i class="fas fa-exclamation-triangle"></i> Threats</h3>
                                <p>${{species.threats || 'Threat information not available.'}}</p>
                            </div>
                            
                            <div style="margin-top: 2rem;">
                                <h3><i class="fas fa-book"></i> Description</h3>
                                <p>${{species.description || 'Detailed description not available.'}}</p>
                            </div>
                        `;
                        
                        document.getElementById('modalSpeciesContent').innerHTML = content;
                        document.getElementById('speciesModal').style.display = 'block';
                    }}
                    
                    function closeSpeciesModal() {{
                        document.getElementById('speciesModal').style.display = 'none';
                    }}
                    
                    // Close modal when clicking outside
                    window.onclick = function(event) {{
                        const modal = document.getElementById('speciesModal');
                        if (event.target === modal) {{
                            modal.style.display = 'none';
                        }}
                    }}
                </script>
            </body>
            </html>
            '''
        except Exception as e:
            print(f"Error rendering species list: {e}")
            return f"<h1>Error</h1><p>{e}</p>", 500
    
    @app.route('/ai-tools')
    def ai_tools():
        """AI Tools Page"""
        print("AI Tools route called!")
        try:
            return render_template('ai_tools.html')
        except Exception as e:
            print(f"Error loading AI tools template: {e}")
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Tools - FishNet</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 40px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }
                    h1 { color: white; text-align: center; margin-bottom: 30px; }
                    .tools-grid { 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px; 
                        max-width: 1200px; 
                        margin: 0 auto;
                    }
                    .tool-card { 
                        background: white; 
                        padding: 25px; 
                        border-radius: 12px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        transition: transform 0.3s;
                    }
                    .tool-card:hover { transform: translateY(-5px); }
                    .tool-card h3 { color: #2c3e50; margin-top: 0; }
                    .back-btn { 
                        display: inline-block; 
                        margin: 20px auto; 
                        padding: 10px 20px; 
                        background: #3498db; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px;
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <h1>🤖 AI Tools & Analysis</h1>
                <div class="tools-grid">
                    <div class="tool-card">
                        <h3>🔍 Species Identification</h3>
                        <p>AI-powered species identification from images and DNA sequences using advanced computer vision.</p>
                    </div>
                    <div class="tool-card">
                        <h3>📈 Population Analysis</h3>
                        <p>Predictive models for population trends and conservation planning with machine learning algorithms.</p>
                    </div>
                    <div class="tool-card">
                        <h3>🌊 Ocean Health Assessment</h3>
                        <p>Real-time analysis of oceanographic data to assess marine ecosystem health and predict changes.</p>
                    </div>
                    <div class="tool-card">
                        <h3>🧬 DNA Sequencing</h3>
                        <p>Advanced eDNA analysis tools for biodiversity assessment and species detection.</p>
                    </div>
                </div>
                <div style="text-align: center;">
                    <a href="/" class="back-btn">← Back to Home</a>
                </div>
            </body>
            </html>
            '''
    
    @app.route('/data')
    def data():
        """Data Management Page"""
        print("Data route called!")
        try:
            return render_template('data.html')
        except Exception as e:
            print(f"Error loading data template: {e}")
            return f'<h1>Data Page Error</h1><p>{e}</p><a href="/">Home</a>'
    
    @app.route('/map')
    def map_page():
        """Interactive Map Page"""
        print("Map route called!")
        try:
            return render_template('map.html')
        except Exception as e:
            print(f"Error loading map template: {e}")
            return f'<h1>Map Page Error</h1><p>{e}</p><a href="/">Home</a>'
    
    @app.route('/researcher-dashboard')
    def researcher_dashboard():
        """Researcher Dashboard"""
        print("Researcher dashboard route called!")
        try:
            return render_template('researcher_dashboard.html')
        except Exception as e:
            return f'<h1>Researcher Dashboard Error</h1><p>{e}</p><a href="/">Home</a>'
    
    @app.route('/policy-dashboard')
    def policy_dashboard():
        """Policy Maker Dashboard"""
        print("Policy dashboard route called!")
        try:
            return render_template('policy_dashboard.html')
        except Exception as e:
            return f'<h1>Policy Dashboard Error</h1><p>{e}</p><a href="/">Home</a>'
    
    @app.route('/researcher-data')
    def researcher_data():
        return render_template('researcher_data.html')

    @app.route('/researcher-analysis')
    def researcher_analysis():
        return render_template('researcher_analysis.html')

    @app.route('/researcher-maps')
    def researcher_maps():
        return render_template('researcher_maps.html')

    @app.route('/policy-reports')
    def policy_reports():
        return render_template('policy_reports.html')

    @app.route('/policy-alerts')
    def policy_alerts():
        return render_template('policy_alerts.html')

    @app.route('/policy-maps')
    def policy_maps():
        return render_template('policy_maps.html')

    # Lightweight CSV-backed API for prototype counters and lists
    def _root_dir():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    @app.route('/api/species/count')
    def api_species_count():
        try:
            with open(os.path.join(_root_dir(), 'sample-species-data.csv'), 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f) - 1
            return jsonify({'count': max(count, 0)})
        except Exception as e:
            return jsonify({'count': 0, 'error': str(e)}), 500

    @app.route('/api/datasets/count')
    def api_datasets_count():
        # Count sample datasets available
        try:
            files = [
                'sample-species-data.csv',
                'sample-ocean-data.csv',
                'sample-edna-data.csv',
                'coral_reef_surveys.csv',
                'oceanographic_data.csv',
                'edna_sample.csv'
            ]
            present = sum(1 for fn in files if os.path.exists(os.path.join(_root_dir(), fn)))
            return jsonify({'count': present})
        except Exception as e:
            return jsonify({'count': 0, 'error': str(e)}), 500

    @app.route('/api/ocean/datapoints/count')
    def api_ocean_datapoints_count():
        try:
            with open(os.path.join(_root_dir(), 'sample-ocean-data.csv'), 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f) - 1
            return jsonify({'count': max(count, 0)})
        except Exception as e:
            return jsonify({'count': 0, 'error': str(e)}), 500

    @app.route('/api/species/list')
    def api_species_list():
        try:
            data = []
            with open(os.path.join(_root_dir(), 'sample-species-data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return jsonify({'species': data, 'total': len(data)})
        except Exception as e:
            return jsonify({'species': [], 'error': str(e)}), 500

    @app.route('/api/ocean/measurements')
    def api_ocean_measurements():
        """Return ocean measurements from CSV for the map"""
        try:
            measurements = []
            with open(os.path.join(_root_dir(), 'sample-ocean-data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    measurements.append({
                        'latitude': float(r['latitude']),
                        'longitude': float(r['longitude']),
                        'temperature': float(r['temperature_c']),
                        'salinity': float(r['salinity_psu']),
                        'ph': float(r['ph_level']),
                        'recorded_at': r.get('recorded_at'),
                        'region': r.get('region'),
                        'location_name': r.get('location_name')
                    })
            return jsonify({'measurements': measurements})
        except Exception as e:
            return jsonify({'measurements': [], 'error': str(e)}), 500

    @app.route('/api/edna/samples')
    def api_edna_samples():
        """Return eDNA samples from CSV for the map"""
        try:
            samples = []
            with open(os.path.join(_root_dir(), 'sample-edna-data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    # Try to derive a representative species name from dominant_taxa
                    dominant = (r.get('dominant_taxa') or '').split(',')[0].strip()
                    try:
                        total_reads = int(r.get('total_reads') or 0)
                        quality_reads = int(r.get('quality_reads') or 0)
                        confidence = round((quality_reads / total_reads) * 100) if total_reads else 0
                    except Exception:
                        confidence = 0
                    samples.append({
                        'latitude': float(r['latitude']),
                        'longitude': float(r['longitude']),
                        'species_name': dominant,
                        'confidence': confidence,
                        'depth': float(r.get('depth_m') or 0),
                        'collection_date': r.get('collection_date'),
                        'sample_id': r.get('sample_id')
                    })
            return jsonify({'samples': samples})
        except Exception as e:
            return jsonify({'samples': [], 'error': str(e)}), 500

    @app.route('/api/species/occurrences')
    def api_species_occurrences():
        """Approximate species occurrences from eDNA CSV (prototype)"""
        try:
            occurrences = []
            with open(os.path.join(_root_dir(), 'sample-edna-data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    dominant = (r.get('dominant_taxa') or '').split(',')[0].strip()
                    occurrences.append({
                        'species_name': dominant,
                        'latitude': float(r['latitude']),
                        'longitude': float(r['longitude']),
                        'abundance': int(r.get('species_detected') or 1),
                        'observed_at': r.get('collection_date')
                    })
            return jsonify({'occurrences': occurrences})
        except Exception as e:
            return jsonify({'occurrences': [], 'error': str(e)}), 500

    @app.route('/api/dashboard/stats')
    def api_dashboard_stats():
        """Stats used by dashboard.js, sourced from CSVs for the prototype"""
        try:
            # Species count
            with open(os.path.join(_root_dir(), 'sample-species-data.csv'), 'r', encoding='utf-8') as f:
                species_count = max(sum(1 for _ in f) - 1, 0)
            # Ocean datapoints
            with open(os.path.join(_root_dir(), 'sample-ocean-data.csv'), 'r', encoding='utf-8') as f:
                ocean_points = max(sum(1 for _ in f) - 1, 0)
            # eDNA total reads
            edna_sequences = 0
            with open(os.path.join(_root_dir(), 'sample-edna-data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    try:
                        edna_sequences += int(r.get('total_reads') or 0)
                    except Exception:
                        pass
            files = [
                'sample-species-data.csv',
                'sample-ocean-data.csv',
                'sample-edna-data.csv',
                'coral_reef_surveys.csv',
                'oceanographic_data.csv',
                'edna_sample.csv'
            ]
            total_datasets = sum(1 for fn in files if os.path.exists(os.path.join(_root_dir(), fn)))
            return jsonify({
                'total_datasets': total_datasets,
                'tracked_species': species_count,
                'active_research': 0,
                'system_health': 'Optimal',
                'ocean_datapoints': ocean_points,
                'edna_sequences': edna_sequences,
                'otolith_images': 0,
                'api_requests_24h': 0
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/datasets/')
    def api_datasets_list():
        """Return recent datasets for dashboard table"""
        try:
            # Return the 3 CSV files as datasets
            datasets = [
                {
                    'id': 1,
                    'dataset_type': 'Species',
                    'region': 'Indian Ocean',
                    'uploaded_at': '2024-01-15',
                    'records_count': 0,
                    'processed': True
                },
                {
                    'id': 2,
                    'dataset_type': 'Ocean',
                    'region': 'Arabian Sea, Bay of Bengal',
                    'uploaded_at': '2024-01-15',
                    'records_count': 0,
                    'processed': True
                },
                {
                    'id': 3,
                    'dataset_type': 'eDNA',
                    'region': 'Indian Ocean',
                    'uploaded_at': '2024-01-15',
                    'records_count': 0,
                    'processed': True
                },
                {
                    'id': 4,
                    'dataset_type': 'Coral',
                    'region': 'Indian Ocean',
                    'uploaded_at': '2025-01-15',
                    'records_count': 0,
                    'processed': True
                }
            ,
                {
                    'id': 5,
                    'dataset_type': 'Ocean',
                    'region': 'Indian Ocean',
                    'uploaded_at': '2025-01-15',
                    'records_count': 0,
                    'processed': True
                }
            ,
                {
                    'id': 6,
                    'dataset_type': 'eDNA',
                    'region': 'Indian Ocean',
                    'uploaded_at': '2025-01-15',
                    'records_count': 0,
                    'processed': True
                }
            ]
            
            # Get actual counts
            try:
                with open(os.path.join(_root_dir(), 'sample-species-data.csv'), 'r', encoding='utf-8') as f:
                    datasets[0]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            
            try:
                with open(os.path.join(_root_dir(), 'sample-ocean-data.csv'), 'r', encoding='utf-8') as f:
                    datasets[1]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            
            try:
                with open(os.path.join(_root_dir(), 'sample-edna-data.csv'), 'r', encoding='utf-8') as f:
                    datasets[2]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            
            try:
                with open(os.path.join(_root_dir(), 'coral_reef_surveys.csv'), 'r', encoding='utf-8') as f:
                    datasets[3]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            
            # Extra oceanographic dataset count (oceanographic_data.csv)
            try:
                with open(os.path.join(_root_dir(), 'oceanographic_data.csv'), 'r', encoding='utf-8') as f:
                    datasets[4]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            # Extra eDNA dataset count (edna_sample.csv)
            try:
                with open(os.path.join(_root_dir(), 'edna_sample.csv'), 'r', encoding='utf-8') as f:
                    datasets[5]['records_count'] = max(sum(1 for _ in f) - 1, 0)
            except: pass
            
            return jsonify({'datasets': datasets})
        except Exception as e:
            return jsonify({'datasets': [], 'error': str(e)}), 500

    @app.route('/api/sea-routes')
    def api_sea_routes():
        """Return sea routes from the database"""
        try:
            routes = SeaRoute.query.all()
            return jsonify({'routes': [r.to_dict() for r in routes]})
        except Exception as e:
            return jsonify({'routes': [], 'error': str(e)}), 500

    # New Coral Reef Surveys API
    @app.route('/api/coral/surveys')
    def api_coral_surveys():
        """Return coral reef survey records from CSV"""
        try:
            surveys = []
            with open(os.path.join(_root_dir(), 'coral_reef_surveys.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    try:
                        surveys.append({
                            'survey_id': r.get('survey_id'),
                            'site_name': r.get('site_name'),
                            'region': r.get('region'),
                            'latitude': float(r['latitude']),
                            'longitude': float(r['longitude']),
                            'survey_date': r.get('survey_date'),
                            'depth_m': float(r.get('depth_m') or 0),
                            'transect_length_m': float(r.get('transect_length_m') or 0),
                            'coral_cover_percent': float(r.get('coral_cover_percent') or 0),
                            'algae_cover_percent': float(r.get('algae_cover_percent') or 0),
                            'bleaching_severity': r.get('bleaching_severity'),
                            'bleached_colonies_percent': float(r.get('bleached_colonies_percent') or 0),
                            'water_temperature_c': float(r.get('water_temperature_c') or 0),
                            'visibility_m': float(r.get('visibility_m') or 0),
                            'current_strength': r.get('current_strength'),
                            'weather_conditions': r.get('weather_conditions')
                        })
                    except Exception:
                        continue
            return jsonify({'surveys': surveys, 'total': len(surveys)})
        except Exception as e:
            return jsonify({'surveys': [], 'error': str(e)}), 500

    # Extra Oceanographic Data API
    @app.route('/api/ocean/measurements2')
    def api_ocean_measurements2():
        """Return ocean measurements from the extra CSV"""
        try:
            measurements = []
            with open(os.path.join(_root_dir(), 'oceanographic_data.csv'), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    try:
                        measurements.append({
                            'latitude': float(r.get('latitude') or r.get('lat') or 0),
                            'longitude': float(r.get('longitude') or r.get('lon') or r.get('lng') or 0),
                            'temperature': float(r.get('temperature_c') or r.get('temperature') or r.get('temp') or 0),
                            'salinity': float(r.get('salinity_psu') or r.get('salinity') or 0),
                            'ph': float(r.get('ph_level') or r.get('ph') or 0),
                            'recorded_at': r.get('recorded_at') or r.get('date') or r.get('datetime'),
                            'region': r.get('region') or r.get('area') or r.get('location'),
                            'location_name': r.get('location_name') or r.get('site') or r.get('station')
                        })
                    except Exception:
                        continue
            return jsonify({'measurements': measurements})
        except Exception as e:
            return jsonify({'measurements': [], 'error': str(e)}), 500

    print("Main routes registered, now setting up API...")
    
    # =============================================================================
    # API SETUP (After main routes)
    # =============================================================================
    
    # Initialize Flask-RESTx API with custom path
    api = Api(app, version='1.0', title='FishNet API', 
              description='Marine Biodiversity Platform API',
              doc='/api-docs/')
    
    # Import and register dashboard namespace
    try:
        from app.routes.dashboard import dashboard_ns
        api.add_namespace(dashboard_ns, path='/api/dashboard')
        print("Dashboard API routes registered")
    except ImportError as e:
        print(f"Dashboard API routes not found: {e}")
    
    # Register other API namespaces
    try:
        from app.routes.species import species_ns
        api.add_namespace(species_ns, path='/api/species')
        print("Species API routes registered")
    except ImportError as e:
        print(f"Species API routes not found: {e}")
    
    try:
        from app.routes.datasets import datasets_ns
        api.add_namespace(datasets_ns, path='/api/datasets')
        print("Datasets API routes registered")
    except ImportError as e:
        print(f"Datasets API routes not found: {e}")
    
    try:
        from app.routes.ocean import ocean_ns
        api.add_namespace(ocean_ns, path='/api/ocean')
        print("Ocean API routes registered")
    except ImportError as e:
        print(f"Ocean API routes not found: {e}")
    
    try:
        from app.routes.edna import edna_ns
        api.add_namespace(edna_ns, path='/api/edna')
        print("eDNA API routes registered")
    except ImportError as e:
        print(f"eDNA API routes not found: {e}")
    
    try:
        from app.routes.data_management import data_ns
        api.add_namespace(data_ns, path='/api/data')
        print("Data management API routes registered")
    except ImportError as e:
        print(f"Data management API routes not found: {e}")

    try:
        from app.routes.prediction import prediction_ns
        api.add_namespace(prediction_ns, path='/api/predict')
        print("Prediction API routes registered")
    except ImportError as e:
        print(f"Prediction API routes not found: {e}")

    # Register Supabase routes
    try:
        from app.routes.supabase import supabase_ns
        api.add_namespace(supabase_ns, path='/api/supabase')
        print("Supabase API routes registered")
    except ImportError as e:
        print(f"Supabase API routes not found: {e}")
    
    print("App setup complete!")
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    return app