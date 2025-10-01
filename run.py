from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Skip database creation for now - we'll use Supabase directly
    print("Starting FishNet Marine Biodiversity Platform...")
    print("Visit: http://localhost:5000")
    print("Use /api/supabase/create-tables to get SQL for table creation")
    print("Use /api/supabase/migrate-csv to migrate CSV data to Supabase")
    
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)