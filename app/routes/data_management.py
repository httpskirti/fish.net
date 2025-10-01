"""
Data Management API Routes
"""
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from sqlalchemy import func, distinct
from ..models import db, Species, OceanographicData, EdnaSample, Dataset
from ..services.data_loader import DataLoader

data_ns = Namespace('data', description='Data management operations')

# Initialize data loader
data_loader = DataLoader()

@data_ns.route('/load-sample-data')
class LoadSampleData(Resource):
    def post(self):
        """Load sample CSV data into database"""
        try:
            results = data_loader.load_sample_data()
            return {
                'success': True,
                'message': 'Sample data loaded successfully',
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500

@data_ns.route('/summary')
class DataSummary(Resource):
    def get(self):
        """Get data summary statistics"""
        try:
            summary = data_loader.get_data_summary()
            return summary
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/researcher/summary')
class ResearcherSummary(Resource):
    def get(self):
        """Get researcher dashboard summary"""
        try:
            # Return mock data while migrating to Supabase
            return {
                'species_count': 10,
                'threatened_species': 3,
                'commercial_species': 5,
                'ocean_datapoints': 15,
                'avg_temperature': 26.5,
                'avg_ph': 8.1,
                'avg_salinity': 35.2,
                'avg_oxygen': 6.8,
                'edna_samples': 8,
                'avg_diversity': 2.45,
                'total_species_detected': 67,
                'avg_reads': 45000
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/policy/summary')
class PolicySummary(Resource):
    def get(self):
        """Get policy dashboard summary"""
        try:
            # Return mock data while migrating to Supabase
            return {
                'critical_species': 2,
                'commercial_risk': 3,
                'protected_areas': 5,
                'trend_positive': 4,
                'declining_species': 3,
                'stable_species': 2,
                'increasing_species': 5
            }
            
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/species/distribution')
class SpeciesDistribution(Resource):
    def get(self):
        """Get species distribution data for mapping"""
        try:
            # Return mock distribution data while migrating to Supabase
            distribution_data = [
                {
                    'scientific_name': 'Sardinella longiceps',
                    'common_name': 'Indian Oil Sardine',
                    'conservation_status': 'Least Concern',
                    'latitude': 15.12,
                    'longitude': 73.54,
                    'location': 'Mumbai Nearshore',
                    'count': 50
                },
                {
                    'scientific_name': 'Rastrelliger kanagurta',
                    'common_name': 'Indian Mackerel',
                    'conservation_status': 'Least Concern',
                    'latitude': 12.85,
                    'longitude': 74.88,
                    'location': 'Mangalore Coast',
                    'count': 35
                }
            ]
            
            return {'distribution_data': distribution_data}
            
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/ocean/parameters')
class OceanParameters(Resource):
    def get(self):
        """Get ocean parameter data for mapping"""
        try:
            # Return mock ocean parameters data while migrating to Supabase
            parameters_data = [
                {
                    'latitude': 15.12,
                    'longitude': 73.54,
                    'location': 'Mumbai Nearshore',
                    'temperature': 26.5,
                    'ph': 8.1,
                    'salinity': 35.2,
                    'oxygen': 6.8,
                    'recorded_at': '2024-07-15T10:30:00'
                },
                {
                    'latitude': 12.85,
                    'longitude': 74.88,
                    'location': 'Mangalore Coast',
                    'temperature': 27.2,
                    'ph': 8.0,
                    'salinity': 34.8,
                    'oxygen': 7.1,
                    'recorded_at': '2024-07-16T09:15:00'
                }
            ]
            
            return {'parameters_data': parameters_data}
            
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/edna/sites')
class EdnaSites(Resource):
    def get(self):
        """Get eDNA sampling sites data for mapping"""
        try:
            # Return mock eDNA sites data while migrating to Supabase
            sites_data = [
                {
                    'sample_id': 'EDNA-IOD-001',
                    'latitude': 15.12,
                    'longitude': 73.54,
                    'location': 'Mumbai Nearshore',
                    'species_detected': 67,
                    'shannon_diversity': 2.45,
                    'total_reads': 47523,
                    'collection_date': '2024-07-15'
                },
                {
                    'sample_id': 'EDNA-IOD-002',
                    'latitude': 12.85,
                    'longitude': 74.88,
                    'location': 'Mangalore Coast',
                    'species_detected': 52,
                    'shannon_diversity': 2.12,
                    'total_reads': 38945,
                    'collection_date': '2024-07-16'
                }
            ]
            
            return {'sites_data': sites_data}
            
        except Exception as e:
            return {'error': str(e)}, 500

@data_ns.route('/upload', methods=['POST'])
class DataUpload(Resource):
    def post(self):
        """Upload and process data files"""
        try:
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Get form data
            dataset_name = request.form.get('name', file.filename)
            dataset_type = request.form.get('type', 'Other')
            region = request.form.get('region', '')
            description = request.form.get('description', '')
            
            # Save file temporarily and process
            # In a real implementation, you would:
            # 1. Save the file securely
            # 2. Validate the file format
            # 3. Process the data based on type
            # 4. Store in database
            
            # For demo, return success
            return {
                'success': True,
                'message': f'File {file.filename} uploaded successfully',
                'dataset_name': dataset_name,
                'dataset_type': dataset_type,
                'region': region,
                'description': description
            }
            
        except Exception as e:
            return {'error': str(e)}, 500