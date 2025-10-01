#!/usr/bin/env python3
"""
Supabase Data Migration Script
Run this script to migrate your CSV data to Supabase database
"""

import pandas as pd
import os
import sys
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ehduimetxekjnsafoupw.supabase.co"
# Use service role key for data insertion (has more permissions)
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZHVpbWV0eGVram5zYWZvdXB3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODcyMTA3OCwiZXhwIjoyMDc0Mjk3MDc4fQ.YOUR_SERVICE_ROLE_KEY_HERE"

# Note: You need to get your service role key from Supabase dashboard
# Go to: Project Settings > API > service_role key (secret)
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZHVpbWV0eGVram5zYWZvdXB3Iiwicm9sZSI6ImFub24iLCJpXCI6InVwYW1hdHVyZXZhbHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MjEwNzgsImV4cCI6MjA3NDI5NzA3OH0.DhowGooRASMJcg1VefFd831RlHDx-hP5XFsZ8gedZK8"

def create_supabase_client():
    """Create and return Supabase client"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def migrate_species_data(supabase, file_path):
    """Migrate species CSV to Supabase"""
    print("🐟 Migrating species data...")
    
    if not os.path.exists(file_path):
        return {'error': f'Species CSV file not found: {file_path}'}
    
    df = pd.read_csv(file_path)
    print(f"   Found {len(df)} species records")
    
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
    
    try:
        # Insert dataset
        dataset_result = supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
            print(f"   Created dataset record with ID: {dataset_id}")
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
        batch_size = 50  # Smaller batch size for better reliability
        inserted_count = 0
        
        for i in range(0, len(species_records), batch_size):
            batch = species_records[i:i + batch_size]
            try:
                result = supabase.table('species').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
                    print(f"   Inserted batch {i//batch_size + 1}: {len(result.data)} records")
            except Exception as e:
                print(f"   Error inserting species batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"✅ Species migration completed: {inserted_count}/{len(df)} records")
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}
        
    except Exception as e:
        print(f"❌ Error migrating species data: {e}")
        return {'error': str(e)}

def migrate_ocean_data(supabase, file_path):
    """Migrate ocean CSV to Supabase"""
    print("🌊 Migrating oceanographic data...")
    
    if not os.path.exists(file_path):
        return {'error': f'Ocean CSV file not found: {file_path}'}
    
    df = pd.read_csv(file_path)
    print(f"   Found {len(df)} oceanographic records")
    
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
    
    try:
        dataset_result = supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
            print(f"   Created dataset record with ID: {dataset_id}")
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
        batch_size = 50
        inserted_count = 0
        
        for i in range(0, len(ocean_records), batch_size):
            batch = ocean_records[i:i + batch_size]
            try:
                result = supabase.table('oceanographic_data').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
                    print(f"   Inserted batch {i//batch_size + 1}: {len(result.data)} records")
            except Exception as e:
                print(f"   Error inserting ocean batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"✅ Ocean data migration completed: {inserted_count}/{len(df)} records")
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}
        
    except Exception as e:
        print(f"❌ Error migrating ocean data: {e}")
        return {'error': str(e)}

def migrate_edna_data(supabase, file_path):
    """Migrate eDNA CSV to Supabase"""
    print("🧬 Migrating eDNA data...")
    
    if not os.path.exists(file_path):
        return {'error': f'eDNA CSV file not found: {file_path}'}
    
    df = pd.read_csv(file_path)
    print(f"   Found {len(df)} eDNA records")
    
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
    
    try:
        dataset_result = supabase.table('datasets').insert(dataset_data).execute()
        if dataset_result.data:
            dataset_id = dataset_result.data[0]['id']
            print(f"   Created dataset record with ID: {dataset_id}")
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
        batch_size = 50
        inserted_count = 0
        
        for i in range(0, len(edna_records), batch_size):
            batch = edna_records[i:i + batch_size]
            try:
                result = supabase.table('edna_samples').insert(batch).execute()
                if result.data:
                    inserted_count += len(result.data)
                    print(f"   Inserted batch {i//batch_size + 1}: {len(result.data)} records")
            except Exception as e:
                print(f"   Error inserting eDNA batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"✅ eDNA migration completed: {inserted_count}/{len(df)} records")
        return {'success': True, 'records': inserted_count, 'dataset_id': dataset_id}
        
    except Exception as e:
        print(f"❌ Error migrating eDNA data: {e}")
        return {'error': str(e)}

def main():
    """Main migration function"""
    print("🚀 Starting Supabase Data Migration")
    print("=" * 50)
    
    # Create Supabase client
    supabase = create_supabase_client()
    if not supabase:
        print("❌ Failed to create Supabase client. Exiting.")
        sys.exit(1)
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # File paths
    species_file = os.path.join(current_dir, 'sample-species-data.csv')
    ocean_file = os.path.join(current_dir, 'sample-ocean-data.csv')
    edna_file = os.path.join(current_dir, 'sample-edna-data.csv')
    
    results = {}
    
    # Migrate species data
    if os.path.exists(species_file):
        results['species'] = migrate_species_data(supabase, species_file)
    else:
        print(f"⚠️  Species file not found: {species_file}")
        results['species'] = {'error': 'File not found'}
    
    print()
    
    # Migrate ocean data
    if os.path.exists(ocean_file):
        results['ocean'] = migrate_ocean_data(supabase, ocean_file)
    else:
        print(f"⚠️  Ocean file not found: {ocean_file}")
        results['ocean'] = {'error': 'File not found'}
    
    print()
    
    # Migrate eDNA data
    if os.path.exists(edna_file):
        results['edna'] = migrate_edna_data(supabase, edna_file)
    else:
        print(f"⚠️  eDNA file not found: {edna_file}")
        results['edna'] = {'error': 'File not found'}
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION SUMMARY")
    print("=" * 50)
    
    total_records = 0
    for data_type, result in results.items():
        if 'success' in result and result['success']:
            records = result.get('records', 0)
            total_records += records
            print(f"✅ {data_type.upper()}: {records} records migrated successfully")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ {data_type.upper()}: Migration failed - {error}")
    
    print(f"\n🎉 Total records migrated: {total_records}")
    print("\n✨ Migration completed! Your data is now available in Supabase.")
    print("\n🔗 Check your data at: https://supabase.com/dashboard")

if __name__ == "__main__":
    main()