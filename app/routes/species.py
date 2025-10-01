"""
Species API Routes - Enhanced with Real Data Integration
"""
import json
from flask import request
from flask_restx import Namespace, Resource, fields
from ..models import db, Species, SpeciesOccurrence, Dataset
from sqlalchemy import func, or_, desc
from datetime import datetime

species_ns = Namespace('species', description='Marine species operations')

# API models
species_model = species_ns.model('Species', {
    'id': fields.Integer(description='Species ID'),
    'scientific_name': fields.String(description='Scientific name'),
    'common_name': fields.String(description='Common name'),
    'family': fields.String(description='Taxonomic family'),
    'habitat': fields.String(description='Primary habitat'),
    'conservation_status': fields.String(description='Conservation status'),
    'commercial_importance': fields.String(description='Commercial importance'),
    'max_length_cm': fields.Float(description='Maximum length in cm'),
    'trophic_level': fields.Float(description='Trophic level')
})

@species_ns.route('/')
class SpeciesList(Resource):
    def get(self):
        """Get all species with filtering and pagination"""
        try:
            # Get query parameters
            family = request.args.get('family')
            status = request.args.get('status')
            habitat = request.args.get('habitat')
            commercial = request.args.get('commercial')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            # Build query
            query = Species.query
            
            if family:
                query = query.filter(Species.family.ilike(f'%{family}%'))
            
            if status:
                query = query.filter(Species.conservation_status.ilike(f'%{status}%'))
            
            if habitat:
                query = query.filter(Species.habitat.ilike(f'%{habitat}%'))
            
            if commercial:
                query = query.filter(Species.commercial_importance.ilike(f'%{commercial}%'))
            
            # Order by scientific name
            species = query.order_by(Species.scientific_name).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            species_list = []
            for s in species.items:
                s_dict = s.to_dict()
                s_dict['image_url'] = f"/static/images/species/{s.scientific_name.lower().replace(' ', '_')}.jpg"
                species_list.append(s_dict)

            return {
                'species': species_list,
                'pagination': {
                    'total': species.total,
                    'pages': species.pages,
                    'current_page': page,
                    'per_page': per_page
                },
                'filters_applied': {
                    'family': family,
                    'status': status,
                    'habitat': habitat,
                    'commercial': commercial
                }
            }
            
        except Exception as e:
            species_ns.abort(500, f"Error retrieving species: {str(e)}")

@species_ns.route('/search')
class SpeciesSearch(Resource):
    def get(self):
        """Search species by name with autocomplete support"""
        try:
            query = request.args.get('q', '').strip()
            limit = request.args.get('limit', 20, type=int)
            
            if not query or len(query) < 2:
                return {
                    'results': [],
                    'message': 'Please provide at least 2 characters for search'
                }
            
            # Search across multiple fields
            species = Species.query.filter(
                or_(
                    Species.scientific_name.ilike(f'%{query}%'),
                    Species.common_name.ilike(f'%{query}%'),
                    Species.family.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results = []
            for s in species:
                # Calculate match score for ranking
                score = 0
                if query.lower() in s.scientific_name.lower():
                    score += 3
                if s.common_name and query.lower() in s.common_name.lower():
                    score += 2
                if s.family and query.lower() in s.family.lower():
                    score += 1
                
                results.append({
                    'id': s.id,
                    'scientific_name': s.scientific_name,
                    'common_name': s.common_name,
                    'family': s.family,
                    'conservation_status': s.conservation_status,
                    'commercial_importance': s.commercial_importance,
                    'habitat': s.habitat,
                    'match_score': score
                })
            
            # Sort by match score
            results = sorted(results, key=lambda x: x['match_score'], reverse=True)
            
            return {
                'results': results,
                'count': len(results),
                'query': query
            }
            
        except Exception as e:
            species_ns.abort(500, f"Species search error: {str(e)}")

@species_ns.route('/<int:species_id>')
class SpeciesDetail(Resource):
    def get(self, species_id):
        """Get detailed species information with occurrence data"""
        try:
            species = Species.query.get(species_id)
            if not species:
                species_ns.abort(404, f"Species with ID {species_id} not found")
            
            # Get occurrence statistics
            occurrence_stats = db.session.query(
                func.count(SpeciesOccurrence.id).label('total_observations'),
                func.avg(SpeciesOccurrence.abundance).label('avg_abundance'),
                func.sum(SpeciesOccurrence.biomass_kg).label('total_biomass'),
                func.min(SpeciesOccurrence.observed_at).label('first_observation'),
                func.max(SpeciesOccurrence.observed_at).label('last_observation')
            ).filter(SpeciesOccurrence.species_id == species_id).first()
            
            # Get recent occurrences for mapping
            recent_occurrences = SpeciesOccurrence.query.filter(
                SpeciesOccurrence.species_id == species_id
            ).order_by(desc(SpeciesOccurrence.observed_at)).limit(20).all()
            
            # Get geographic distribution
            geographic_range = db.session.query(
                func.min(SpeciesOccurrence.latitude).label('min_lat'),
                func.max(SpeciesOccurrence.latitude).label('max_lat'),
                func.min(SpeciesOccurrence.longitude).label('min_lng'),
                func.max(SpeciesOccurrence.longitude).label('max_lng')
            ).filter(SpeciesOccurrence.species_id == species_id).first()
            
            # Compile comprehensive species data
            species_data = species.to_dict()
            species_data['image_url'] = f"/static/images/species/{species.scientific_name.lower().replace(' ', '_')}.jpg"
            species_data.update({
                'occurrence_statistics': {
                    'total_observations': occurrence_stats.total_observations or 0,
                    'average_abundance': float(occurrence_stats.avg_abundance or 0),
                    'total_biomass_kg': float(occurrence_stats.total_biomass or 0),
                    'first_observation': occurrence_stats.first_observation.isoformat() if occurrence_stats.first_observation else None,
                    'last_observation': occurrence_stats.last_observation.isoformat() if occurrence_stats.last_observation else None
                },
                'geographic_range': {
                    'min_latitude': float(geographic_range.min_lat) if geographic_range.min_lat else None,
                    'max_latitude': float(geographic_range.max_lat) if geographic_range.max_lat else None,
                    'min_longitude': float(geographic_range.min_lng) if geographic_range.min_lng else None,
                    'max_longitude': float(geographic_range.max_lng) if geographic_range.max_lng else None
                },
                'recent_locations': [
                    {
                        'latitude': occ.latitude,
                        'longitude': occ.longitude,
                        'abundance': occ.abundance,
                        'date': occ.observed_at.isoformat() if occ.observed_at else None,
                        'method': occ.survey_method,
                        'observer': occ.observer
                    } for occ in recent_occurrences
                ]
            })
            
            return species_data
            
        except Exception as e:
            species_ns.abort(500, f"Error retrieving species details: {str(e)}")

@species_ns.route('/families')
class SpeciesFamilies(Resource):
    def get(self):
        """Get taxonomic families with species counts"""
        try:
            families = db.session.query(
                Species.family,
                func.count(Species.id).label('species_count'),
                func.count(func.distinct(Species.genus)).label('genus_count')
            ).filter(Species.family.isnot(None)).group_by(Species.family).order_by(Species.family).all()
            
            return {
                'families': [
                    {
                        'family': family.family,
                        'species_count': family.species_count,
                        'genus_count': family.genus_count
                    } for family in families
                ],
                'total_families': len(families)
            }
            
        except Exception as e:
            species_ns.abort(500, f"Error retrieving families: {str(e)}")

@species_ns.route('/identify')
class SpeciesIdentification(Resource):
    def post(self):
        """Identify species from an uploaded image using Gemini AI"""
        if 'file' not in request.files:
            return {'message': 'No file part'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        try:
            # Import AI service
            from ..services.ai_service import AIService
            
            # Read image data
            image_data = file.read()
            
            # Initialize AI service
            ai_service = AIService()
            
            # Identify species using Gemini AI
            result = ai_service.identify_species_from_image(image_data, file.filename)
            
            if result['success']:
                # Format response for frontend
                species_list = result['data'].get('species_identified', [])
                formatted_results = []
                
                for species in species_list:
                    formatted_results.append({
                        "scientific_name": species.get('scientific_name', 'Unknown'),
                        "common_name": species.get('common_name', 'Unknown'),
                        "family": species.get('family', 'Unknown'),
                        "confidence": species.get('confidence', 0),
                        "conservation_status": species.get('conservation_status', 'Unknown'),
                        "habitat": species.get('habitat', 'Marine environment'),
                        "identifying_features": species.get('identifying_features', [])
                    })
                
                return {
                    "success": True,
                    "results": formatted_results,
                    "analysis_notes": result['data'].get('analysis_notes', ''),
                    "image_quality": result['data'].get('image_quality', 'Good')
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to identify species'),
                    "results": []
                }, 500
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}",
                "results": []
            }, 500

@species_ns.route('/occurrences')
class SpeciesOccurrences(Resource):
    def get(self):
        """Get all species occurrences"""
        try:
            occurrences = SpeciesOccurrence.query.all()
            return {
                'occurrences': [o.to_dict() for o in occurrences]
            }
        except Exception as e:
            species_ns.abort(500, f"Error retrieving species occurrences: {str(e)}")

@species_ns.route('/conservation-summary')
class ConservationSummary(Resource):
    def get(self):
        """Get conservation status summary with trend analysis"""
        try:
            # Conservation status counts
            status_counts = db.session.query(
                Species.conservation_status,
                func.count(Species.id).label('count')
            ).group_by(Species.conservation_status).all()
            
            # Commercial importance breakdown
            commercial_counts = db.session.query(
                Species.commercial_importance,
                func.count(Species.id).label('count')
            ).filter(Species.commercial_importance.isnot(None)).group_by(Species.commercial_importance).all()
            
            # Endemic species count
            endemic_count = Species.query.filter_by(endemic_to_indian_ocean=True).count()
            
            return {
                'conservation_status': {
                    status.conservation_status: status.count 
                    for status in status_counts if status.conservation_status
                },
                'commercial_importance': {
                    comm.commercial_importance: comm.count
                    for comm in commercial_counts
                },
                'endemic_species': endemic_count,
                'total_species': Species.query.count(),
                'summary': {
                    'threatened_species': sum(
                        status.count for status in status_counts 
                        if status.conservation_status in ['Near Threatened', 'Vulnerable', 'Endangered', 'Critically Endangered']
                    ),
                    'commercially_important': sum(
                        comm.count for comm in commercial_counts
                        if comm.commercial_importance in ['High', 'Very High']
                    )
                }
            }
            
        except Exception as e:
            species_ns.abort(500, f"Error generating conservation summary: {str(e)}")