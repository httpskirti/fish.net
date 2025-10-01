#!/usr/bin/env python3
"""
Test Flask Application Supabase Connection
Run this script to test if your Flask app can connect to Supabase
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from flask import Flask
from backend.config import Config
from supabase import create_client

def test_supabase_connection():
    """Test Supabase connection using Flask config"""
    print("🧪 Testing Flask-Supabase Connection")
    print("=" * 50)
    
    try:
        # Create Supabase client using Flask config
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        print(f"✅ Supabase client created successfully")
        print(f"   URL: {Config.SUPABASE_URL}")
        
        # Test connection by querying datasets
        result = supabase.table('datasets').select('count').execute()
        print(f"✅ Database connection successful")
        
        # Count records in each table
        tables = ['datasets', 'species', 'oceanographic_data', 'edna_samples']
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').execute()
                count = len(result.data) if result.data else 0
                print(f"   📊 {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_flask_app_startup():
    """Test if Flask app can start with Supabase config"""
    print("\n🚀 Testing Flask App Startup")
    print("-" * 30)
    
    try:
        # Import Flask app components
        from backend.app import create_app
        
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test app context
        with app.app_context():
            print("✅ Flask app context working")
            
            # Test if Supabase is accessible in app context
            if hasattr(app, 'supabase'):
                print("✅ Supabase client available in app context")
            else:
                print("⚠️  Supabase client not found in app context")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app startup failed: {e}")
        return False

def test_database_queries():
    """Test sample database queries that your app might use"""
    print("\n🔍 Testing Sample Database Queries")
    print("-" * 35)
    
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
        
        # Test species query (like your species page might use)
        print("Testing species query...")
        species_result = supabase.table('species').select('scientific_name, common_name, conservation_status').limit(5).execute()
        if species_result.data:
            print(f"✅ Species query successful: {len(species_result.data)} records")
            for species in species_result.data[:2]:
                print(f"   - {species['scientific_name']} ({species['common_name']})")
        else:
            print("⚠️  No species data found")
        
        # Test ocean data query (like your dashboard might use)
        print("\nTesting ocean data query...")
        ocean_result = supabase.table('oceanographic_data').select('latitude, longitude, temperature_c').limit(5).execute()
        if ocean_result.data:
            print(f"✅ Ocean data query successful: {len(ocean_result.data)} records")
            for record in ocean_result.data[:2]:
                temp = record.get('temperature_c', 'N/A')
                print(f"   - Location: ({record['latitude']}, {record['longitude']}) - {temp}°C")
        else:
            print("⚠️  No ocean data found")
        
        # Test eDNA query (like your eDNA page might use)
        print("\nTesting eDNA query...")
        edna_result = supabase.table('edna_samples').select('sample_id, species_detected, shannon_diversity').limit(5).execute()
        if edna_result.data:
            print(f"✅ eDNA query successful: {len(edna_result.data)} records")
            for sample in edna_result.data[:2]:
                diversity = sample.get('shannon_diversity', 'N/A')
                species_count = sample.get('species_detected', 'N/A')
                print(f"   - Sample {sample['sample_id']}: {species_count} species, diversity: {diversity}")
        else:
            print("⚠️  No eDNA data found")
        
        return True
        
    except Exception as e:
        print(f"❌ Database queries failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Flask-Supabase Integration Test")
    print("=" * 50)
    
    # Run tests
    connection_ok = test_supabase_connection()
    flask_ok = test_flask_app_startup()
    queries_ok = test_database_queries()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    tests_passed = sum([connection_ok, flask_ok, queries_ok])
    total_tests = 3
    
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        print("✨ Your Flask app is ready to work with Supabase!")
        print("\n🚀 Next steps:")
        print("   1. Run your Flask app: python backend/run.py")
        print("   2. Visit http://localhost:5000 to see your app")
        print("   3. Check that data displays correctly on all pages")
        
    elif tests_passed > 0:
        print("⚠️  Some tests passed, others failed.")
        print("📖 Check the errors above and fix any issues.")
        
    else:
        print("❌ All tests failed.")
        print("📖 Please check your Supabase configuration and data migration.")
    
    print(f"\n🔗 Supabase Dashboard: https://supabase.com/dashboard")

if __name__ == "__main__":
    main()