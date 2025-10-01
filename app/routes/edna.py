"""
eDNA Analysis API Routes
Handles environmental DNA sample data and analysis
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from ..models import db, EdnaSample, Dataset
from sqlalchemy import func, desc
from datetime import datetime

edna_ns = Namespace('edna', description='Environmental DNA analysis operations')

# API models
edna_model = edna_ns.model('EdnaSample', {
    'id': fields.Integer(description='Sample ID'),
    'sample_id': fields.String(description='Sample identifier'),
    'latitude': fields.Float(description='Sample latitude'),
    'longitude': fields.Float(description='Sample longitude'),
    'collection_date': fields.Date(description='Sample collection date'),
    'species_detected': fields.Integer(description='Number of species detected'),
    'shannon_diversity': fields.Float(description='Shannon diversity index'),
    'total_reads': fields.Integer(description='Total DNA reads'),
    'processing_lab': fields.String(description='Processing laboratory')
})

@edna_ns.route('/')
class EdnaList(Resource):
    @edna_ns.marshal_list_with(edna_model)
    def get(self):
        """Get all eDNA samples with filtering options"""
        try:
            # Get query parameters
            lab = request.args.get('lab')
            min_species = request.args.get('min_species', type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            # Build query
            query = EdnaSample.query
            
            if lab:
                query = query.filter(EdnaSample.processing_lab.ilike(f'%{lab}%'))
            
            if min_species:
                query = query.filter(EdnaSample.species_detected >= min_species)
            
            # Order by collection date (newest first)
            samples = query.order_by(desc(EdnaSample.collection_date)).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'samples': [s.to_dict() for s in samples.items],
                'pagination': {
                    'total': samples.total,
                    'pages': samples.pages,
                    'current_page': page
                }
            }
            
        except Exception as e:
            edna_ns.abort(500, f"Error retrieving eDNA samples: {str(e)}")

@edna_ns.route('/samples')
class EdnaSamples(Resource):
    def get(self):
        """Get all eDNA samples"""
        try:
            samples = EdnaSample.query.all()
            return {
                'samples': [s.to_dict() for s in samples]
            }
        except Exception as e:
            edna_ns.abort(500, f"Error retrieving eDNA samples: {str(e)}")

@edna_ns.route('/biodiversity-summary')
class BiodiversitySummary(Resource):
    def get(self):
        """Get biodiversity summary from eDNA data"""
        try:
            # Overall statistics
            total_samples = EdnaSample.query.count()
            total_species_detected = db.session.query(func.sum(EdnaSample.species_detected)).scalar() or 0
            avg_diversity = db.session.query(func.avg(EdnaSample.shannon_diversity)).scalar() or 0
            
            # Regional breakdown
            regional_stats = db.session.query(
                EdnaSample.processing_lab,
                func.count(EdnaSample.id).label('sample_count'),
                func.avg(EdnaSample.species_detected).label('avg_species'),
                func.avg(EdnaSample.shannon_diversity).label('avg_diversity')
            ).group_by(EdnaSample.processing_lab).all()
            
            return {
                'overall_stats': {
                    'total_samples': total_samples,
                    'total_species_detected': int(total_species_detected),
                    'average_diversity': round(float(avg_diversity), 3)
                },
                'regional_breakdown': [
                    {
                        'lab': stat.processing_lab,
                        'sample_count': stat.sample_count,
                        'avg_species_per_sample': round(float(stat.avg_species or 0), 1),
                        'avg_diversity_index': round(float(stat.avg_diversity or 0), 3)
                    } for stat in regional_stats if stat.processing_lab
                ]
            }
            
        except Exception as e:
            edna_ns.abort(500, f"Error generating biodiversity summary: {str(e)}")