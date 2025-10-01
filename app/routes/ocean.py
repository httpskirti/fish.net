"""
Ocean Data API Routes - Oceanographic Measurements and Analysis
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from ..models import db, OceanographicData, Dataset
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

ocean_ns = Namespace('ocean', description='Oceanographic data operations')

# API models
ocean_model = ocean_ns.model('OceanographicData', {
    'id': fields.Integer(description='Data point ID'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'region': fields.String(description='Geographic region'),
    'depth_m': fields.Float(description='Water depth in meters'),
    'temperature_c': fields.Float(description='Water temperature in Celsius'),
    'salinity_psu': fields.Float(description='Salinity in PSU'),
    'ph_level': fields.Float(description='pH level'),
    'recorded_at': fields.DateTime(description='Measurement timestamp')
})

@ocean_ns.route('/data')
class OceanDataList(Resource):
    def get(self):
        """Get oceanographic measurements with filtering"""
        try:
            # Get query parameters
            region = request.args.get('region')
            min_depth = request.args.get('min_depth', type=float)
            max_depth = request.args.get('max_depth', type=float)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            
            # Build query
            query = OceanographicData.query
            
            if region:
                query = query.filter(OceanographicData.region.ilike(f'%{region}%'))
            
            if min_depth is not None:
                query = query.filter(OceanographicData.depth_m >= min_depth)
            
            if max_depth is not None:
                query = query.filter(OceanographicData.depth_m <= max_depth)
            
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', ''))
                    query = query.filter(OceanographicData.recorded_at >= start_dt)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', ''))
                    query = query.filter(OceanographicData.recorded_at <= end_dt)
                except ValueError:
                    pass
            
            # Execute query with pagination
            data = query.order_by(desc(OceanographicData.recorded_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'data': [d.to_dict() for d in data.items],
                'pagination': {
                    'total': data.total,
                    'pages': data.pages,
                    'current_page': page,
                    'per_page': per_page
                },
                'filters_applied': {
                    'region': region,
                    'depth_range': f"{min_depth}-{max_depth}m" if min_depth or max_depth else None,
                    'date_range': f"{start_date} to {end_date}" if start_date or end_date else None
                }
            }
            
        except Exception as e:
            ocean_ns.abort(500, f"Error retrieving ocean data: {str(e)}")

@ocean_ns.route('/measurements')
class OceanMeasurements(Resource):
    def get(self):
        """Get all oceanographic measurements"""
        try:
            measurements = OceanographicData.query.all()
            return {
                'measurements': [m.to_dict() for m in measurements]
            }
        except Exception as e:
            ocean_ns.abort(500, f"Error retrieving ocean measurements: {str(e)}")

@ocean_ns.route('/summary')
class OceanDataSummary(Resource):
    def get(self):
        """Get summary statistics for oceanographic parameters"""
        try:
            # Parameter statistics
            stats = db.session.query(
                func.count(OceanographicData.id).label('total_measurements'),
                func.min(OceanographicData.temperature_c).label('min_temp'),
                func.max(OceanographicData.temperature_c).label('max_temp'),
                func.avg(OceanographicData.temperature_c).label('avg_temp'),
                func.min(OceanographicData.depth_m).label('min_depth'),
                                func.max(OceanographicData.depth_m).label('max_depth'),
                func.avg(OceanographicData.depth_m).label('avg_depth'),
                func.avg(OceanographicData.salinity_psu).label('avg_salinity'),
                func.avg(OceanographicData.ph_level).label('avg_ph'),
                func.avg(OceanographicData.dissolved_oxygen_ml_l).label('avg_oxygen'),
                func.avg(OceanographicData.chlorophyll_a_mg_m3).label('avg_chlorophyll')
            ).first()
            
            # Regional coverage
            regions = db.session.query(
                OceanographicData.region,
                func.count(OceanographicData.id).label('measurement_count')
            ).filter(OceanographicData.region.isnot(None)).group_by(OceanographicData.region).all()
            
            # Data sources
            sources = db.session.query(
                OceanographicData.data_source,
                func.count(OceanographicData.id).label('measurement_count')
            ).filter(OceanographicData.data_source.isnot(None)).group_by(OceanographicData.data_source).all()
            
            return {
                'parameter_statistics': {
                    'total_measurements': stats.total_measurements,
                    'temperature_c': {
                        'min': float(stats.min_temp) if stats.min_temp else None,
                        'max': float(stats.max_temp) if stats.max_temp else None,
                        'average': round(float(stats.avg_temp), 2) if stats.avg_temp else None
                    },
                    'depth_m': {
                        'min': float(stats.min_depth) if stats.min_depth else None,
                        'max': float(stats.max_depth) if stats.max_depth else None,
                        'average': round(float(stats.avg_depth), 2) if stats.avg_depth else None
                    },
                    'salinity_psu': {
                        'average': round(float(stats.avg_salinity), 2) if stats.avg_salinity else None
                    },
                    'ph_level': {
                        'average': round(float(stats.avg_ph), 2) if stats.avg_ph else None
                    },
                    'dissolved_oxygen_ml_l': {
                        'average': round(float(stats.avg_oxygen), 2) if stats.avg_oxygen else None
                    },
                    'chlorophyll_a_mg_m3': {
                        'average': round(float(stats.avg_chlorophyll), 3) if stats.avg_chlorophyll else None
                    }
                },
                'regional_coverage': [
                    {
                        'region': region.region,
                        'measurement_count': region.measurement_count
                    } for region in regions
                ],
                'data_sources': [
                    {
                        'source': source.data_source,
                        'measurement_count': source.measurement_count
                    } for source in sources
                ]
            }
            
        except Exception as e:
            ocean_ns.abort(500, f"Error generating ocean data summary: {str(e)}")