#!/usr/bin/env python3
"""
Load sample data into the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.data_loader import DataLoader

def main():
    print("Loading sample data into FishNet database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Initialize data loader
        data_loader = DataLoader()
        
        # Load sample data
        results = data_loader.load_sample_data()
        
        print("\n=== Data Loading Results ===")
        for data_type, result in results.items():
            if 'error' in result:
                print(f"❌ {data_type.title()}: {result['error']}")
            else:
                print(f"✅ {data_type.title()}: {result['records']} records loaded")
        
        # Get summary
        summary = data_loader.get_data_summary()
        print(f"\n=== Database Summary ===")
        print(f"Total Datasets: {summary.get('datasets', 0)}")
        print(f"Total Species: {summary.get('species', 0)}")
        print(f"Ocean Data Points: {summary.get('ocean_data', 0)}")
        print(f"eDNA Samples: {summary.get('edna_samples', 0)}")
        print(f"Regions: {summary.get('regions', 0)}")
        
        print("\n🎉 Sample data loaded successfully!")
        print("You can now access the full functionality at http://localhost:5000")

if __name__ == '__main__':
    main()