"""
Supabase Migration Service - Migrate CSV data to Supabase database
"""
import pandas as pd
import os
from flask import current_app
from datetime import datetime
from ..models import db, Species, OceanographicData, EdnaSample, Dataset

class SupabaseMigrator:
    def __init__(self):
        self.supabase = current_app.supabase
        
    def create_tables_in_supabase(self):
        """Create tables in Supabase using SQL"""
        
        # Species table
        species_sql = """
        CREATE TABLE IF NOT EXISTS species (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER,
            scientific_name VARCHAR(150) NOT NULL,
            common_name VARCHAR(150),
            kingdom VARCHAR(50) DEFAULT 'Animalia',
            phylum VARCHAR(50),
            class_name VARCHAR(50),
            order_name VARCHAR(50),
            family VARCHAR(50),
            genus VARCHAR(50),
            species VARCHAR(50),
            max_length_cm FLOAT,
            max_weight_kg FLOAT,
            average_lifespan_years INTEGER,
            body_shape VARCHAR(100),
            habitat VARCHAR(100),
            diet VARCHAR(200),
            trophic_level FLOAT,
            feeding_behavior VARCHAR(100),
            reproduction_type VARCHAR(100),
            conservation_status VARCHAR(50),
            population_trend VARCHAR(50),
            threats TEXT,
            protection_status VARCHAR(100),
            commercial_importance VARCHAR(20),
            fishing_methods TEXT,
            market_value_usd_kg FLOAT,
            fishery_status VARCHAR(50),
            endemic_to_indian_ocean BOOLEAN DEFAULT FALSE,
            depth_range_min_m FLOAT,
            depth_range_max_m FLOAT,
            temperature_range_min_c FLOAT,
            temperature_range_max_c FLOAT,
            salinity_tolerance VARCHAR(50),
            geographic_distribution TEXT,
            image_url VARCHAR(500),
            thumbnail_url VARCHAR(500),
            description TEXT,
            identification_features TEXT,
            similar_species TEXT,
            data_source VARCHAR(100),
            source_id VARCHAR(100),
            last_updated TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Ocean data table
        ocean_sql = """
        CREATE TABLE IF NOT EXISTS oceanographic_data (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            location_name VARCHAR(100),
            region VARCHAR(100),
            country VARCHAR(100),
            depth_m FLOAT,
            temperature_c FLOAT,
            salinity_psu FLOAT,
            ph_level FLOAT,
            dissolved_oxygen_ml_l FLOAT,
            turbidity_ntu FLOAT,
            conductivity FLOAT,
            nitrate_mg_l FLOAT,
            phosphate_mg_l FLOAT,
            silicate_mg_l FLOAT,
            chlorophyll_a_mg_m3 FLOAT,
            total_nitrogen FLOAT,
            total_phosphorus FLOAT,
            primary_productivity FLOAT,
            bacterial_count INTEGER,
            phytoplankton_abundance FLOAT,
            zooplankton_abundance FLOAT,
            water_current_speed_ms FLOAT,
            water_current_direction FLOAT,
            wave_height_m FLOAT,
            wind_speed_ms FLOAT,
            wind_direction FLOAT,
            recorded_at TIMESTAMP NOT NULL,
            measurement_depth_m FLOAT,
            sampling_method VARCHAR(100),
            instrument_type VARCHAR(100),
            data_source VARCHAR(100),
            quality_flag VARCHAR(20) DEFAULT 'good',
            air_temperature_c FLOAT,
            weather_conditions VARCHAR(100),
            sea_state VARCHAR(50),
            visibility_km FLOAT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # eDNA samples table
        edna_sql = """
        CREATE TABLE IF NOT EXISTS edna_samples (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER,
            sample_id VARCHAR(50) UNIQUE NOT NULL,
            field_sample_id VARCHAR(50),
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            depth_m FLOAT,
            location_description VARCHAR(200),
            collection_date DATE NOT NULL,
            collection_time TIME,
            collector VARCHAR(100),
            collection_method VARCHAR(100),
            sample_volume_l FLOAT,
            filtration_method VARCHAR(100),
            filter_type VARCHAR(50),
            filter_pore_size_um FLOAT,
            processing_lab VARCHAR(100),
            extraction_date DATE,
            extraction_method VARCHAR(100),
            pcr_primers VARCHAR(200),
            sequencing_platform VARCHAR(100),
            library_prep_method VARCHAR(100),
            total_reads INTEGER,
            quality_reads INTEGER,
            unique_sequences INTEGER,
            species_detected INTEGER,
            shannon_diversity FLOAT,
            simpson_diversity FLOAT,
            species_richness INTEGER,
            evenness_index FLOAT,
            detected_species_json TEXT,
            sequence_data_json TEXT,
            taxonomy_summary_json TEXT,
            water_temperature_c FLOAT,
            salinity_psu FLOAT,
            ph_level FLOAT,
            dissolved_oxygen_ml_l FLOAT,
            turbidity_ntu FLOAT,
            negative_control BOOLEAN DEFAULT FALSE,
            positive_control BOOLEAN DEFAULT FALSE,
            extraction_blank BOOLEAN DEFAULT FALSE,
            pcr_blank BOOLEAN DEFAULT FALSE,
            contamination_check VARCHAR(50),
            quality_score FLOAT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Datasets table
        datasets_sql = """
        CREATE TABLE IF NOT EXISTS datasets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            dataset_type VARCHAR(50),
            source_type VARCHAR(50),
            original_filename VARCHAR(200),
            file_path VARCHAR(500),
            file_size_mb FLOAT,
            description TEXT,
            region VARCHAR(100),
            collection_start_date DATE,
            collection_end_date DATE,
            data_source_organization VARCHAR(200),
            uploaded_at TIMESTAMP DEFAULT NOW(),
            processed BOOLEAN DEFAULT FALSE,
            processing_errors TEXT,
            records_count INTEGER DEFAULT 0,
            data_quality_score FLOAT,
            completeness_percentage FLOAT,
            api_endpoint VARCHAR(500),
            last_sync TIMESTAMP,
            sync_status VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute SQL commands
        try:
            # Note: Supabase Python client doesn't support raw SQL execution
            # You need to create these tables manually in Supabase SQL Editor
            # or use the Supabase dashboard
            print("Tables need to be created manually in Supabase SQL Editor:")
            print("1. Go to your Supabase dashboard")
            print("2. Navigate to SQL Editor")
            print("3. Execute the following SQL commands:")
            print("\n" + species_sql)
            print("\n" + ocean_sql)
            print("\n" + edna_sql)
            print("\n" + datasets_sql)
            
            return True
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    def migrate_csv_to_supabase(self):
        """Migrate all CSV data to Supabase"""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        results = {}
        
        # Migrate species data
        try:
            species_file = os.path.join(project_root, 'sample-species-data.csv')
            if os.path.exists(species_file):
                results['species'] = self._migrate_species_data(species_file)
            else:
                results['species'] = {'error': 'Species CSV file not found'}
        except Exception as e:
            results['species'] = {'error': str(e)}
        
        # Migrate ocean data
        try:
            ocean_file = os.path.join(project_root, 'sample-ocean-data.csv')
            if os.path.exists(ocean_file):
                results['ocean'] = self._migrate_ocean_data(ocean_file)
            else:
                results['ocean'] = {'error': 'Ocean CSV file not found'}
        except Exception as e:
            results['ocean'] = {'error': str(e)}
        
        # Migrate eDNA data
        try:
            edna_file = os.path.join(project_root, 'sample-edna-data.csv')
            if os.path.exists(edna_file):
                results['edna'] = self._migrate_edna_data(edna_file)
            else:
                results['edna'] = {'error': 'eDNA CSV file not found'}
        except Exception as e:
            results['edna'] = {'error': str(e)}
        
        return results
    
    def _migrate_species_data(self, file_path):
        """Migrate species CSV to Supabase"""
        df = pd.read_csv(file_path)
        
        # Create dataset record first
        dataset_data = {
            'name': 'Sample Species Data - Migrated',
            'dataset_type': 'Species',
            'source_type': 'CSV Migration',
            'original_filename': 'sample-species-data.csv',
            'description': 'Marine species data migrated from CSV to Supabase',
            'region': 'Indian Ocean',
            'processed': True,
            'data_quality_score': 0.95,
            'records_count': len(df)
        }
        
        # Insert dataset
        dataset_result = self.supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
        else:
            return {'error': 'Failed to create dataset record'}
        
        # Prepare species data
        species_records = []
        for _, row in df.iterrows():
            species_record = {
                'dataset_id': dataset_id,
                'scientific_name': row.get('scientific_name'),
                'common_name': row.get('common_name'),
                'family': row.get('family'),
                'genus': row.get('genus'),
                'order_name': row.get('order'),
                'class_name': row.get('class'),
                'phylum': row.get('phylum'),
                'kingdom': row.get('kingdom', 'Animalia'),
                'habitat': row.get('habitat'),
                'conservation_status': row.get('conservation_status'),
                'max_length_cm': float(row['max_length_cm']) if pd.notna(row.get('max_length_cm')) else None,
                'trophic_level': float(row['trophic_level']) if pd.notna(row.get('trophic_level')) else None,
                'depth_range_min_m': float(row['depth_min_m']) if pd.notna(row.get('depth_min_m')) else None,
                'depth_range_max_m': float(row['depth_max_m']) if pd.notna(row.get('depth_max_m')) else None,
                'temperature_range_min_c': float(row['temperature_min_c']) if pd.notna(row.get('temperature_min_c')) else None,
                'temperature_range_max_c': float(row['temperature_max_c']) if pd.notna(row.get('temperature_max_c')) else None,
                'commercial_importance': row.get('commercial_importance'),
                'description': row.get('description'),
                'threats': row.get('threats'),
                'geographic_distribution': row.get('distribution'),
                'data_source': 'CSV Migration'
            }
            species_records.append(species_record)
        
        # Insert species data in batches
        batch_size = 100
        inserted_count = 0
        
        for i in range(0, len(species_records), batch_size):
            batch = species_records[i:i + batch_size]
            try:
                result = self.supabase.table('species').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
            except Exception as e:
                print(f"Error inserting species batch: {e}")
                continue
        
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}
    
    def _migrate_ocean_data(self, file_path):
        """Migrate ocean CSV to Supabase"""
        df = pd.read_csv(file_path)
        
        # Create dataset record
        dataset_data = {
            'name': 'Sample Ocean Data - Migrated',
            'dataset_type': 'Ocean',
            'source_type': 'CSV Migration',
            'original_filename': 'sample-ocean-data.csv',
            'description': 'Oceanographic data migrated from CSV to Supabase',
            'region': 'Indian Ocean',
            'processed': True,
            'data_quality_score': 0.92,
            'records_count': len(df)
        }
        
        dataset_result = self.supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
        else:
            return {'error': 'Failed to create dataset record'}
        
        # Prepare ocean data
        ocean_records = []
        for _, row in df.iterrows():
            ocean_record = {
                'dataset_id': dataset_id,
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'region': row.get('region'),
                'depth_m': float(row['depth_m']) if pd.notna(row.get('depth_m')) else None,
                'temperature_c': float(row['temperature_c']) if pd.notna(row.get('temperature_c')) else None,
                'salinity_psu': float(row['salinity_psu']) if pd.notna(row.get('salinity_psu')) else None,
                'ph_level': float(row['ph_level']) if pd.notna(row.get('ph_level')) else None,
                'dissolved_oxygen_ml_l': float(row['dissolved_oxygen_ml_l']) if pd.notna(row.get('dissolved_oxygen_ml_l')) else None,
                'nitrate_mg_l': float(row['nitrate_mg_l']) if pd.notna(row.get('nitrate_mg_l')) else None,
                'phosphate_mg_l': float(row['phosphate_mg_l']) if pd.notna(row.get('phosphate_mg_l')) else None,
                'chlorophyll_a_mg_m3': float(row['chlorophyll_a_mg_m3']) if pd.notna(row.get('chlorophyll_a_mg_m3')) else None,
                'turbidity_ntu': float(row['turbidity_ntu']) if pd.notna(row.get('turbidity_ntu')) else None,
                'recorded_at': pd.to_datetime(row['recorded_at']).isoformat() if pd.notna(row.get('recorded_at')) else None,
                'location_name': row.get('location_name'),
                'data_source': row.get('data_source', 'CSV Migration'),
                'quality_flag': row.get('quality_flag', 'good')
            }
            ocean_records.append(ocean_record)
        
        # Insert ocean data in batches
        batch_size = 100
        inserted_count = 0
        
        for i in range(0, len(ocean_records), batch_size):
            batch = ocean_records[i:i + batch_size]
            try:
                result = self.supabase.table('oceanographic_data').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
            except Exception as e:
                print(f"Error inserting ocean batch: {e}")
                continue
        
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}
    
    def _migrate_edna_data(self, file_path):
        """Migrate eDNA CSV to Supabase"""
        df = pd.read_csv(file_path)
        
        # Create dataset record
        dataset_data = {
            'name': 'Sample eDNA Data - Migrated',
            'dataset_type': 'eDNA',
            'source_type': 'CSV Migration',
            'original_filename': 'sample-edna-data.csv',
            'description': 'Environmental DNA data migrated from CSV to Supabase',
            'region': 'Indian Ocean',
            'processed': True,
            'data_quality_score': 0.88,
            'records_count': len(df)
        }
        
        dataset_result = self.supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
        else:
            return {'error': 'Failed to create dataset record'}
        
        # Prepare eDNA data
        edna_records = []
        for _, row in df.iterrows():
            edna_record = {
                'dataset_id': dataset_id,
                'sample_id': row.get('sample_id'),
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'depth_m': float(row['depth_m']) if pd.notna(row.get('depth_m')) else None,
                'collection_date': pd.to_datetime(row['collection_date']).date().isoformat() if pd.notna(row.get('collection_date')) else None,
                'total_reads': int(row['total_reads']) if pd.notna(row.get('total_reads')) else None,
                'quality_reads': int(row['quality_reads']) if pd.notna(row.get('quality_reads')) else None,
                'species_detected': int(row['species_detected']) if pd.notna(row.get('species_detected')) else None,
                'shannon_diversity': float(row['shannon_diversity']) if pd.notna(row.get('shannon_diversity')) else None,
                'simpson_diversity': float(row['simpson_diversity']) if pd.notna(row.get('simpson_diversity')) else None,
                'processing_lab': row.get('processing_lab'),
                'sequencing_platform': row.get('sequencing_platform'),
                'location_description': row.get('location_name'),
                'detected_species_json': f'{{"dominant_taxa": "{row.get("dominant_taxa", "")}", "rare_taxa_count": {row.get("rare_taxa_count", 0)}, "environmental_conditions": "{row.get("environmental_conditions", "")}"}}' if pd.notna(row.get('dominant_taxa')) else None
            }
            edna_records.append(edna_record)
        
        # Insert eDNA data in batches
        batch_size = 100
        inserted_count = 0
        
        for i in range(0, len(edna_records), batch_size):
            batch = edna_records[i:i + batch_size]
            try:
                result = self.supabase.table('edna_samples').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
            except Exception as e:
                print(f"Error inserting eDNA batch: {e}")
                continue
        
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}