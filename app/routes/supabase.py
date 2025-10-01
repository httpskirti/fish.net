"""
Supabase Integration Routes
Fetch subsets from Supabase and store in local DB
"""
from flask import Blueprint, jsonify, request, current_app
from flask_restx import Namespace, Resource, fields
from ..services.supabase_service import SupabaseService
from ..services.supabase_migrator import SupabaseMigrator
from ..models import db

supabase_ns = Namespace('supabase', description='Supabase integration operations')

# Model for fetch request
fetch_model = supabase_ns.model('FetchRequest', {
    'table': fields.String(required=True, description='Supabase table name'),
    'filters': fields.Raw(description='Key-value filter dict'),
    'limit': fields.Integer(description='Max records to fetch')
})

@supabase_ns.route('/fetch')
class SupabaseFetch(Resource):
    @supabase_ns.expect(fetch_model)
    def post(self):
        """Fetch data from Supabase"""
        payload = request.json or {}
        table = payload.get('table')
        filters = payload.get('filters')
        limit = payload.get('limit')
        service = SupabaseService()
        data = service.fetch_table(table, filters=filters, limit=limit)
        return jsonify({'fetched': len(data), 'data': data})

# Model for storing species subset
store_model = supabase_ns.model('StoreSpeciesRequest', {
    'filters': fields.Raw(description='Filters for species'),
    'limit': fields.Integer(description='Limit number of species')
})

@supabase_ns.route('/store-species')
class StoreSpecies(Resource):
    @supabase_ns.expect(store_model)
    def post(self):
        """Fetch species subset from Supabase and store locally"""
        payload = request.json or {}
        filters = payload.get('filters')
        limit = payload.get('limit')
        service = SupabaseService()
        created = service.store_species_subset(filters=filters, limit=limit)
        return jsonify({'stored': len(created)})

@supabase_ns.route('/migrate-csv')
class MigrateCSV(Resource):
    def post(self):
        """Migrate all CSV data to Supabase database"""
        try:
            migrator = SupabaseMigrator()
            results = migrator.migrate_csv_to_supabase()
            return jsonify({
                'success': True,
                'migration_results': results,
                'message': 'CSV data migration completed'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@supabase_ns.route('/create-tables')
class CreateTables(Resource):
    def post(self):
        """Create tables in Supabase (instructions only)"""
        try:
            migrator = SupabaseMigrator()
            result = migrator.create_tables_in_supabase()
            return jsonify({
                'success': result,
                'message': 'Check console for SQL commands to run in Supabase'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
