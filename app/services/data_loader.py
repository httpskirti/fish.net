"""
Data Loader Service - Import CSV data into database
"""
import pandas as pd
import os
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from ..models import db, Species, OceanographicData, EdnaSample, Dataset

class DataLoader:
    def __init__(self, app=None):
        self.app = app
        
    def load_sample_data(self):
        """Load all sample CSV files into database"""
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            results = {
                'species': self.load_species_data(os.path.join(project_root, 'sample-species-data.csv')),
                'ocean': self.load_ocean_data(os.path.join(project_root, 'sample-ocean-data.csv')),
                'edna': self.load_edna_data(os.path.join(project_root, 'sample-edna-data.csv'))
            }
            
            return results
            
        except Exception as e:
            print(f"Error loading sample data: {e}")
            return {'error': str(e)}
    
    def load_species_data(self, file_path):
        """Load species data from CSV"""
        try:
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
                
            # Create dataset record
            dataset = Dataset(
                name="Sample Species Data",
                dataset_type="Species",
                source_type="Upload",
                original_filename="sample-species-data.csv",
                description="Sample marine species data for Indian Ocean",
                region="Indian Ocean",
                processed=True,
                data_quality_score=0.95
            )
            db.session.add(dataset)
            db.session.flush()  # Get the ID
            
            # Read CSV
            df = pd.read_csv(file_path)
            species_count = 0
            
            for _, row in df.iterrows():
                try:
                    species = Species(
                        dataset_id=dataset.id,
                        scientific_name=row['scientific_name'],
                        common_name=row['common_name'],
                        family=row['family'],
                        genus=row['genus'],
                        order=row['order'],
                        class_name=row['class'],
                        phylum=row['phylum'],
                        kingdom=row['kingdom'],
                        habitat=row['habitat'],
                        conservation_status=row['conservation_status'],
                        max_length_cm=float(row['max_length_cm']) if pd.notna(row['max_length_cm']) else None,
                        trophic_level=float(row['trophic_level']) if pd.notna(row['trophic_level']) else None,
                        depth_range_min_m=float(row['depth_min_m']) if pd.notna(row['depth_min_m']) else None,
                        depth_range_max_m=float(row['depth_max_m']) if pd.notna(row['depth_max_m']) else None,
                        temperature_range_min_c=float(row['temperature_min_c']) if pd.notna(row['temperature_min_c']) else None,
                        temperature_range_max_c=float(row['temperature_max_c']) if pd.notna(row['temperature_max_c']) else None,
                        commercial_importance=row['commercial_importance'],
                        description=row['description'],
                        threats=row['threats'],
                        geographic_distribution=row['distribution'],
                        data_source="Sample Data"
                    )
                    db.session.add(species)
                    species_count += 1
                except Exception as e:
                    print(f"Error adding species {row.get('scientific_name', 'unknown')}: {e}")
                    continue
            
            dataset.records_count = species_count
            db.session.commit()
            
            return {'success': True, 'records': species_count, 'dataset_id': dataset.id}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def load_ocean_data(self, file_path):
        """Load oceanographic data from CSV"""
        try:
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
                
            # Create dataset record
            dataset = Dataset(
                name="Sample Ocean Data",
                dataset_type="Ocean",
                source_type="Upload",
                original_filename="sample-ocean-data.csv",
                description="Sample oceanographic data for Indian Ocean",
                region="Indian Ocean",
                processed=True,
                data_quality_score=0.92
            )
            db.session.add(dataset)
            db.session.flush()
            
            # Read CSV
            df = pd.read_csv(file_path)
            ocean_count = 0
            
            for _, row in df.iterrows():
                try:
                    ocean_data = OceanographicData(
                        dataset_id=dataset.id,
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        region=row['region'],
                        depth_m=float(row['depth_m']) if pd.notna(row['depth_m']) else None,
                        temperature_c=float(row['temperature_c']) if pd.notna(row['temperature_c']) else None,
                        salinity_psu=float(row['salinity_psu']) if pd.notna(row['salinity_psu']) else None,
                        ph_level=float(row['ph_level']) if pd.notna(row['ph_level']) else None,
                        dissolved_oxygen_ml_l=float(row['dissolved_oxygen_ml_l']) if pd.notna(row['dissolved_oxygen_ml_l']) else None,
                        nitrate_mg_l=float(row['nitrate_mg_l']) if pd.notna(row['nitrate_mg_l']) else None,
                        phosphate_mg_l=float(row['phosphate_mg_l']) if pd.notna(row['phosphate_mg_l']) else None,
                        chlorophyll_a_mg_m3=float(row['chlorophyll_a_mg_m3']) if pd.notna(row['chlorophyll_a_mg_m3']) else None,
                        turbidity_ntu=float(row['turbidity_ntu']) if pd.notna(row['turbidity_ntu']) else None,
                        recorded_at=pd.to_datetime(row['recorded_at']),
                        location_name=row['location_name'],
                        data_source=row['data_source'],
                        quality_flag=row['quality_flag']
                    )
                    db.session.add(ocean_data)
                    ocean_count += 1
                except Exception as e:
                    print(f"Error adding ocean data for {row.get('location_name', 'unknown')}: {e}")
                    continue
            
            dataset.records_count = ocean_count
            db.session.commit()
            
            return {'success': True, 'records': ocean_count, 'dataset_id': dataset.id}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def load_edna_data(self, file_path):
        """Load eDNA data from CSV"""
        try:
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
                
            # Create dataset record
            dataset = Dataset(
                name="Sample eDNA Data",
                dataset_type="eDNA",
                source_type="Upload",
                original_filename="sample-edna-data.csv",
                description="Sample environmental DNA data for Indian Ocean",
                region="Indian Ocean",
                processed=True,
                data_quality_score=0.88
            )
            db.session.add(dataset)
            db.session.flush()
            
            # Read CSV
            df = pd.read_csv(file_path)
            edna_count = 0
            
            for _, row in df.iterrows():
                try:
                    edna_sample = EdnaSample(
                        dataset_id=dataset.id,
                        sample_id=row['sample_id'],
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        depth_m=float(row['depth_m']) if pd.notna(row['depth_m']) else None,
                        collection_date=pd.to_datetime(row['collection_date']).date(),
                        total_reads=int(row['total_reads']) if pd.notna(row['total_reads']) else None,
                        quality_reads=int(row['quality_reads']) if pd.notna(row['quality_reads']) else None,
                        species_detected=int(row['species_detected']) if pd.notna(row['species_detected']) else None,
                        shannon_diversity=float(row['shannon_diversity']) if pd.notna(row['shannon_diversity']) else None,
                        simpson_diversity=float(row['simpson_diversity']) if pd.notna(row['simpson_diversity']) else None,
                        processing_lab=row['processing_lab'],
                        sequencing_platform=row['sequencing_platform'],
                        location_description=row['location_name'],
                        detected_species_json=f'{{"dominant_taxa": "{row["dominant_taxa"]}", "rare_taxa_count": {row["rare_taxa_count"]}, "environmental_conditions": "{row["environmental_conditions"]}"}}' if pd.notna(row['dominant_taxa']) else None
                    )
                    db.session.add(edna_sample)
                    edna_count += 1
                except Exception as e:
                    print(f"Error adding eDNA sample {row.get('sample_id', 'unknown')}: {e}")
                    continue
            
            dataset.records_count = edna_count
            db.session.commit()
            
            return {'success': True, 'records': edna_count, 'dataset_id': dataset.id}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def get_data_summary(self):
        """Get summary of loaded data"""
        try:
            summary = {
                'datasets': Dataset.query.count(),
                'species': Species.query.count(),
                'ocean_data': OceanographicData.query.count(),
                'edna_samples': EdnaSample.query.count(),
                'regions': db.session.query(OceanographicData.region).distinct().count(),
                'conservation_status': db.session.query(Species.conservation_status).distinct().all()
            }
            return summary
        except Exception as e:
            return {'error': str(e)}