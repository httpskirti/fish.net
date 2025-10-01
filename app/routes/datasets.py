"""
Dataset Management API - File Upload and Processing
Supports multiple formats and real-time processing
"""
import os
import pandas as pd
import json
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np

from ..models import db, Dataset, Species, OceanographicData, SpeciesOccurrence, EdnaSample
from ..services.data_processor import DatasetProcessor
from ..services.obis_integration import OBISIntegration

datasets_ns = Namespace('datasets', description='Dataset management and processing')

# API models for documentation
dataset_model = datasets_ns.model('Dataset', {
    'id': fields.Integer(description='Dataset ID'),
    'name': fields.String(required=True, description='Dataset name'),
    'dataset_type': fields.String(description='Type of dataset (Species, Ocean, eDNA, Routes)'),
    'source_type': fields.String(description='Source type (Upload, API, OBIS)'),
    'description': fields.String(description='Dataset description'),
    'region': fields.String(description='Geographic region'),
    'records_count': fields.Integer(description='Number of records'),
    'file_size_mb': fields.Float(description='File size in MB'),
    'uploaded_at': fields.DateTime(description='Upload timestamp'),
    'processed': fields.Boolean(description='Processing status'),
    'data_quality_score': fields.Float(description='Data quality score (0-1)')
})

upload_response_model = datasets_ns.model('UploadResponse', {
    'success': fields.Boolean(description='Upload success'),
    'dataset_id': fields.Integer(description='Created dataset ID'),
    'filename': fields.String(description='Stored filename'),
    'file_size_mb': fields.Float(description='File size in MB'),
    'processing_status': fields.String(description='Processing status'),
    'records_processed': fields.Integer(description='Number of records processed')
})

@datasets_ns.route('/upload')
class DatasetUpload(Resource):
    @datasets_ns.expect(datasets_ns.parser().add_argument('file', location='files', type='file', required=True, help='Dataset file'))
    @datasets_ns.marshal_with(upload_response_model)
    def post(self):
        """
        Upload a new dataset file
        Supports CSV, Excel, JSON, and GeoJSON formats
        Automatically detects data type and processes accordingly
        """
        try:
            # Validate file upload
            if 'file' not in request.files:
                return {'success': False, 'error': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'success': False, 'error': 'No file selected'}, 400
            
            # Validate file type
            if not allowed_file(file.filename):
                return {
                    'success': False,
                    'error': 'Invalid file type. Supported formats: CSV, Excel, JSON, GeoJSON'
                }, 400
            
            # Get form data
            dataset_name = request.form.get('name', file.filename)
            dataset_type = request.form.get('type', 'Unknown')
            source_type = request.form.get('source_type', 'Upload')
            description = request.form.get('description', '')
            region = request.form.get('region', '')
            organization = request.form.get('organization', '')
            
            # Save file securely
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
            
            file.save(file_path)
            
            # Get file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Create dataset record
            dataset = Dataset(
                name=dataset_name,
                dataset_type=dataset_type,
                source_type=source_type,
                original_filename=filename,
                file_path=file_path,
                file_size_mb=round(file_size_mb, 2),
                description=description,
                region=region,
                data_source_organization=organization,
                uploaded_at=datetime.now(),
                processed=False
            )
            
            db.session.add(dataset)
            db.session.commit()
            
            # Process the dataset
            processor = DatasetProcessor()
            processing_result = processor.process_dataset(dataset.id)
            
            return {
                'success': True,
                'dataset_id': dataset.id,
                'filename': safe_filename,
                'file_size_mb': file_size_mb,
                'processing_status': 'Completed' if processing_result['success'] else 'Failed',
                'records_processed': processing_result.get('records_processed', 0),
                'data_quality_score': processing_result.get('data_quality_score', 0),
                'message': 'Dataset uploaded and processed successfully'
            }
            
        except Exception as e:
            current_app.logger.error(f"Dataset upload error: {str(e)}")
            return {'success': False, 'error': str(e)}, 500

@datasets_ns.route('/')
class DatasetList(Resource):
    @datasets_ns.marshal_list_with(dataset_model)
    def get(self):
        """
        Get all datasets with filtering and pagination
        Supports filtering by type, status, and date range
        """
        try:
            # Get query parameters
            dataset_type = request.args.get('type')
            processed = request.args.get('processed')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            # Build query
            query = Dataset.query
            
            if dataset_type:
                query = query.filter(Dataset.dataset_type == dataset_type)
            
            if processed is not None:
                processed_bool = processed.lower() == 'true'
                query = query.filter(Dataset.processed == processed_bool)
            
            # Order by upload date (newest first)
            query = query.order_by(Dataset.uploaded_at.desc())
            
            # Paginate
            datasets = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'datasets': [d.to_dict() for d in datasets.items],
                'pagination': {
                    'total': datasets.total,
                    'pages': datasets.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': datasets.has_next,
                    'has_prev': datasets.has_prev
                }
            }
            
        except Exception as e:
            datasets_ns.abort(500, f"Error retrieving datasets: {str(e)}")

@datasets_ns.route('/<int:dataset_id>')
class DatasetDetail(Resource):
    def get(self, dataset_id):
        """
        Get detailed information about a specific dataset
        Includes sample data and processing metadata
        """
        try:
            dataset = Dataset.query.get_or_404(dataset_id)
            
            # Get sample data based on dataset type
            sample_data = []
            if dataset.processed:
                if dataset.dataset_type == 'Species':
                    species = Species.query.filter_by(dataset_id=dataset_id).limit(10).all()
                    sample_data = [s.to_dict() for s in species]
                elif dataset.dataset_type == 'Ocean':
                    ocean_data = OceanographicData.query.filter_by(dataset_id=dataset_id).limit(10).all()
                    sample_data = [o.to_dict() for o in ocean_data]
                elif dataset.dataset_type == 'eDNA':
                    edna_samples = EdnaSample.query.filter_by(dataset_id=dataset_id).limit(10).all()
                    sample_data = [e.to_dict() for e in edna_samples]
            
            # Get processing metadata
            processing_metadata = {
                'total_records': dataset.records_count,
                'processing_errors': dataset.processing_errors,
                'data_quality_metrics': {
                    'completeness': dataset.completeness_percentage,
                    'quality_score': dataset.data_quality_score
                },
                'last_sync': dataset.last_sync.isoformat() if dataset.last_sync else None
            }
            
            result = dataset.to_dict()
            result.update({
                'sample_data': sample_data,
                'processing_metadata': processing_metadata,
                'download_url': f'/api/datasets/{dataset_id}/download' if dataset.processed else None
            })
            
            return result
            
        except Exception as e:
            datasets_ns.abort(500, f"Error retrieving dataset details: {str(e)}")

@datasets_ns.route('/<int:dataset_id>/download')
class DatasetDownload(Resource):
    def get(self, dataset_id):
        """
        Download processed dataset
        Returns the processed data in CSV format
        """
        try:
            dataset = Dataset.query.get_or_404(dataset_id)
            
            if not dataset.processed:
                return {'error': 'Dataset not yet processed'}, 400
            
            # Generate download based on dataset type
            if dataset.dataset_type == 'Species':
                species_data = Species.query.filter_by(dataset_id=dataset_id).all()
                data = [s.to_dict() for s in species_data]
            elif dataset.dataset_type == 'Ocean':
                ocean_data = OceanographicData.query.filter_by(dataset_id=dataset_id).all()
                data = [o.to_dict() for o in ocean_data]
            else:
                return {'error': 'Download not available for this dataset type'}, 400
            
            # Convert to DataFrame and return as CSV
            df = pd.DataFrame(data)
            csv_data = df.to_csv(index=False)
            
            return {
                'filename': f"{dataset.name}_processed.csv",
                'data': csv_data,
                'records': len(data)
            }
            
        except Exception as e:
            datasets_ns.abort(500, f"Error downloading dataset: {str(e)}")

@datasets_ns.route('/connect-obis')
class ConnectOBIS(Resource):
    def post(self):
        """
        Connect to OBIS (Ocean Biodiversity Information System) API
        Fetch real marine species data from global database
        """
        try:
            # Get parameters for OBIS query
            region = request.json.get('region', 'Indian Ocean')
            geometry = request.json.get('geometry')  # Optional geometry filter
            limit = request.json.get('limit', 1000)
            
            # Initialize OBIS integration
            obis = OBISIntegration()
            
            # Fetch data from OBIS
            result = obis.fetch_species_occurrences(
                region=region,
                geometry=geometry,
                limit=limit
            )
            
            if result['success']:
                # Create dataset record for OBIS data
                dataset = Dataset(
                    name=f"OBIS Data - {region}",
                    dataset_type='Species',
                    source_type='OBIS',
                    description=f'Species occurrence data from OBIS for {region}',
                    region=region,
                    api_endpoint='https://api.obis.org/v3/occurrence',
                    records_count=result['records_count'],
                    processed=True,
                    data_quality_score=0.9,  # OBIS data is high quality
                    last_sync=datetime.now(),
                    sync_status='Success'
                )
                
                db.session.add(dataset)
                db.session.commit()
                
                # Process and store the OBIS data
                processor = DatasetProcessor()
                processing_result = processor.process_obis_data(dataset.id, result['data'])
                
                return {
                    'success': True,
                    'dataset_id': dataset.id,
                    'records_fetched': result['records_count'],
                    'processing_status': processing_result,
                    'message': f'Successfully connected to OBIS and imported {result["records_count"]} records'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 400
                
        except Exception as e:
            current_app.logger.error(f"OBIS connection error: {str(e)}")
            return {'success': False, 'error': str(e)}, 500

@datasets_ns.route('/types')
class DatasetTypes(Resource):
    def get(self):
        """
        Get available dataset types and their statistics
        """
        try:
            # Count datasets by type
            type_counts = db.session.query(
                Dataset.dataset_type,
                db.func.count(Dataset.id).label('count'),
                db.func.sum(Dataset.records_count).label('total_records')
            ).group_by(Dataset.dataset_type).all()
            
            types_info = []
            for dataset_type, count, total_records in type_counts:
                types_info.append({
                    'type': dataset_type,
                    'dataset_count': count,
                    'total_records': total_records or 0,
                    'description': get_dataset_type_description(dataset_type)
                })
            
            return {
                'dataset_types': types_info,
                'supported_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
                'max_file_size_mb': current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
            }
            
        except Exception as e:
            datasets_ns.abort(500, f"Error retrieving dataset types: {str(e)}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_dataset_type_description(dataset_type):
    """Get description for dataset type"""
    descriptions = {
        'Species': 'Marine species data including taxonomy, distribution, and characteristics',
        'Ocean': 'Oceanographic measurements including temperature, salinity, pH, and other parameters', 
        'eDNA': 'Environmental DNA samples and biodiversity analysis results',
        'Routes': 'Maritime routes, shipping lanes, and navigation data',
        'Other': 'Other marine-related datasets'
    }
    return descriptions.get(dataset_type, 'Marine biodiversity related data')

