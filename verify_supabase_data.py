#!/usr/bin/env python3
"""
Supabase Data Verification Script
Run this script to verify your data was successfully migrated to Supabase
"""

import os
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ehduimetxekjnsafoupw.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZHVpbWV0eGVram5zYWZvdXB3Iiwicm9sZSI6ImFub24iLCJpXCI6InVwYW1hdHVyZXZhbHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MjEwNzgsImV4cCI6MjA3NDI5NzA3OH0.DhowGooRASMJcg1VefFd831RlHDx-hP5XFsZ8gedZK8"

def create_supabase_client():
    """Create and return Supabase client"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        return supabase
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        return None

def verify_datasets(supabase):
    """Verify datasets table"""
    try:
        result = supabase.table('datasets').select('*').execute()
        count = len(result.data) if result.data else 0
        print(f"📊 Datasets: {count} records found")
        
        if result.data:
            for dataset in result.data:
                print(f"   - {dataset['name']} ({dataset['dataset_type']}) - {dataset['records_count']} records")
        
        return count > 0
    except Exception as e:
        print(f"❌ Error checking datasets: {e}")
        return False

def verify_species(supabase):
    """Verify species table"""
    try:
        result = supabase.table('species').select('*').execute()
        count = len(result.data) if result.data else 0
        print(f"🐟 Species: {count} records found")
        
        if result.data:
            # Show sample records
            for i, species in enumerate(result.data[:3]):
                print(f"   - {species['scientific_name']} ({species['common_name']}) - {species['conservation_status']}")
            if count > 3:
                print(f"   ... and {count - 3} more species")
        
        return count > 0
    except Exception as e:
        print(f"❌ Error checking species: {e}")
        return False

def verify_ocean_data(supabase):
    """Verify oceanographic_data table"""
    try:
        result = supabase.table('oceanographic_data').select('*').execute()
        count = len(result.data) if result.data else 0
        print(f"🌊 Oceanographic Data: {count} records found")
        
        if result.data:
            # Show sample records
            for i, record in enumerate(result.data[:3]):
                lat, lon = record['latitude'], record['longitude']
                temp = record.get('temperature_c', 'N/A')
                print(f"   - Location: ({lat}, {lon}) - Temperature: {temp}°C")
            if count > 3:
                print(f"   ... and {count - 3} more records")
        
        return count > 0
    except Exception as e:
        print(f"❌ Error checking ocean data: {e}")
        return False

def verify_edna_data(supabase):
    """Verify edna_samples table"""
    try:
        result = supabase.table('edna_samples').select('*').execute()
        count = len(result.data) if result.data else 0
        print(f"🧬 eDNA Samples: {count} records found")
        
        if result.data:
            # Show sample records
            for i, sample in enumerate(result.data[:3]):
                sample_id = sample['sample_id']
                species_detected = sample.get('species_detected', 'N/A')
                diversity = sample.get('shannon_diversity', 'N/A')
                print(f"   - Sample {sample_id}: {species_detected} species, Shannon diversity: {diversity}")
            if count > 3:
                print(f"   ... and {count - 3} more samples")
        
        return count > 0
    except Exception as e:
        print(f"❌ Error checking eDNA data: {e}")
        return False

def run_sample_queries(supabase):
    """Run some sample analytical queries"""
    print("\n🔍 Running Sample Analytical Queries:")
    print("-" * 40)
    
    try:
        # Conservation status distribution
        result = supabase.table('species').select('conservation_status').execute()
        if result.data:
            status_counts = {}
            for record in result.data:
                status = record.get('conservation_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("Conservation Status Distribution:")
            for status, count in status_counts.items():
                print(f"   - {status}: {count} species")
    except Exception as e:
        print(f"❌ Error in conservation status query: {e}")
    
    try:
        # Average temperature by region
        result = supabase.table('oceanographic_data').select('region, temperature_c').execute()
        if result.data:
            region_temps = {}
            region_counts = {}
            
            for record in result.data:
                region = record.get('region', 'Unknown')
                temp = record.get('temperature_c')
                
                if temp is not None:
                    if region not in region_temps:
                        region_temps[region] = 0
                        region_counts[region] = 0
                    region_temps[region] += temp
                    region_counts[region] += 1
            
            print("\nAverage Temperature by Region:")
            for region in region_temps:
                avg_temp = region_temps[region] / region_counts[region]
                print(f"   - {region}: {avg_temp:.1f}°C")
    except Exception as e:
        print(f"❌ Error in temperature query: {e}")

def main():
    """Main verification function"""
    print("🔍 Supabase Data Verification")
    print("=" * 50)
    
    # Create Supabase client
    supabase = create_supabase_client()
    if not supabase:
        print("❌ Failed to create Supabase client. Exiting.")
        sys.exit(1)
    
    # Verify each table
    datasets_ok = verify_datasets(supabase)
    species_ok = verify_species(supabase)
    ocean_ok = verify_ocean_data(supabase)
    edna_ok = verify_edna_data(supabase)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    total_tables = 4
    working_tables = sum([datasets_ok, species_ok, ocean_ok, edna_ok])
    
    print(f"✅ Working tables: {working_tables}/{total_tables}")
    
    if working_tables == total_tables:
        print("🎉 All tables verified successfully!")
        print("✨ Your Supabase database is ready to use!")
        
        # Run sample queries
        run_sample_queries(supabase)
        
    elif working_tables > 0:
        print("⚠️  Some tables have data, others may need migration.")
        print("📖 Check the migration guide for next steps.")
    else:
        print("❌ No data found in any tables.")
        print("📖 Please follow the migration guide to add data.")
    
    print(f"\n🔗 Supabase Dashboard: https://supabase.com/dashboard")

if __name__ == "__main__":
    main()