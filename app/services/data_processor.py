"""

Dataset Processing Service
Handles processing of uploaded datasets and OBIS data
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
import os

from ..models import db, Dataset, Species, OceanographicData, SpeciesOccurrence, EdnaSample

logger = logging.getLogger(__name__)

class DatasetProcessor:
    """
    Comprehensive dataset processing for multiple data types
    """
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json', 'tsv']
        self.species_columns_map = self._get_species_column_mapping()
        self.ocean_columns_map = self._get_ocean_column_mapping()
    
    def process_dataset(self, dataset_id):
        """
        Main dataset processing function
        
        Args:
            dataset_id: ID of the dataset to process
            
        Returns:
            Processing result dictionary
        """
        try:
            # Get dataset record
            dataset = Dataset.query.get(dataset_id)
            if not dataset:
                return {'success': False, 'error': 'Dataset not found'}
            
            logger.info(f"Processing dataset {dataset_id}: {dataset.name}")
            
            # Load data from file
            df = self._load_dataframe(dataset.file_path)
            if df is None:
                return {'success': False, 'error': 'Failed to load dataset file'}
            
            # Determine dataset type if not specified
            if dataset.dataset_type == 'Unknown':
                dataset.dataset_type = self._detect_dataset_type(df)
            
            # Process based on dataset type
            processing_result = self._process_by_type(dataset, df)
            
            # Update dataset record
            dataset.processed = processing_result['success']
            dataset.records_count = processing_result.get('records_processed', 0)
            dataset.data_quality_score = processing_result.get('data_quality_score', 0)
            dataset.completeness_percentage = processing_result.get('completeness_percentage', 0)
            
            if not processing_result['success']:
                dataset.processing_errors = processing_result.get('error', 'Unknown error')
            
            db.session.commit()
            
            logger.info(f"Dataset {dataset_id} processing completed: {processing_result['success']}")
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing dataset {dataset_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Dataset processing failed: {str(e)}'
            }
    
    def _load_dataframe(self, file_path):
        """Load data file into pandas DataFrame"""
        try:
            file_ext = file_path.split('.')[-1].lower()
            
            if file_ext == 'csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    for sep in [',', ';', '\t']:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                            if len(df.columns) > 1: # Valid CSV
                                return df
                        except:
                            continue
                            
            elif file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
                return df
                
            elif file_ext == 'json':
                df = pd.read_json(file_path)
                return df
                
            elif file_ext == 'tsv':
                df = pd.read_csv(file_path, sep='\t')
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            return None
    
    def _detect_dataset_type(self, df):
        """Auto-detect dataset type based on columns"""
        columns = [col.lower() for col in df.columns]
        
        # Species data indicators
        species_indicators = ['scientific_name', 'species', 'family', 'genus', 'common_name']
        if any(indicator in columns for indicator in species_indicators):
            return 'Species'
        
        # Ocean data indicators
        ocean_indicators = ['temperature', 'salinity', 'ph', 'depth', 'latitude', 'longitude']
        if sum(indicator in ' '.join(columns) for indicator in ocean_indicators) >= 3:
            return 'Ocean'
        
        # eDNA indicators
        edna_indicators = ['sample_id', 'reads', 'sequences', 'diversity']
        if any(indicator in ' '.join(columns) for indicator in edna_indicators):
            return 'eDNA'
        
        return 'Other'
    
    def _process_by_type(self, dataset, df):
        """Process dataset based on its type"""
        if dataset.dataset_type == 'Species':
            return self._process_species_data(dataset, df)
        elif dataset.dataset_type == 'Ocean':
            return self._process_ocean_data(dataset, df)
        elif dataset.dataset_type == 'eDNA':
            return self._process_edna_data(dataset, df)
        else:
            return {
                'success': False,
                'error': f'Unsupported dataset type: {dataset.dataset_type}'
            }
    
    def _process_species_data(self, dataset, df):
        """Process species dataset"""
        try:
            records_added = 0
            
            # Map columns to database fields
            mapped_df = self._map_columns(df, self.species_columns_map)
            
            for _, row in mapped_df.iterrows():
                try:
                    # Check required fields
                    if pd.isna(row.get('scientific_name')):
                        continue
                    
                    # Check if species already exists
                    existing_species = Species.query.filter_by(
                        scientific_name=row['scientific_name']
                    ).first()
                    
                    if existing_species:
                        continue # Skip duplicates
                    
                    # Create new species record
                    species = Species(
                        dataset_id=dataset.id,
                        scientific_name=row.get('scientific_name'),
                        common_name=row.get('common_name'),
                        family=row.get('family'),
                        genus=row.get('genus'),
                        kingdom=row.get('kingdom', 'Animalia'),
                        phylum=row.get('phylum'),
                        class_name=row.get('class'),
                        order=row.get('order'),
                        habitat=row.get('habitat'),
                        conservation_status=row.get('conservation_status'),
                        commercial_importance=row.get('commercial_importance'),
                        max_length_cm=self._safe_float(row.get('max_length_cm')),
                        trophic_level=self._safe_float(row.get('trophic_level')),
                        depth_range_min_m=self._safe_float(row.get('depth_min_m')),
                        depth_range_max_m=self._safe_float(row.get('depth_max_m')),
                        temperature_range_min_c=self._safe_float(row.get('temp_min_c')),
                        temperature_range_max_c=self._safe_float(row.get('temp_max_c')),
                        description=row.get('description'),
                        threats=row.get('threats'),
                        data_source=f'Dataset_{dataset.id}'
                    )
                    
                    db.session.add(species)
                    records_added += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing species row: {e}")
                    continue
            
            db.session.commit()
            
            # Calculate quality metrics
            quality_score = self._calculate_data_quality(df)
            completeness = self._calculate_completeness(df)
            
            return {
                'success': True,
                'records_processed': records_added,
                'data_quality_score': quality_score,
                'completeness_percentage': completeness
            }
            
        except Exception as e:
            logger.error(f"Error processing species data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_ocean_data(self, dataset, df):
        """Process oceanographic dataset"""
        try:
            records_added = 0
            
            # Map columns to database fields
            mapped_df = self._map_columns(df, self.ocean_columns_map)
            
            for _, row in mapped_df.iterrows():
                try:
                    # Check required fields
                    if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')):
                        continue
                    
                    # Create oceanographic data record
                    ocean_data = OceanographicData(
                        dataset_id=dataset.id,
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        depth_m=self._safe_float(row.get('depth_m')),
                        temperature_c=self._safe_float(row.get('temperature_c')),
                        salinity_psu=self._safe_float(row.get('salinity_psu')),
                        ph_level=self._safe_float(row.get('ph_level')),
                        dissolved_oxygen_ml_l=self._safe_float(row.get('dissolved_oxygen_ml_l')),
                        chlorophyll_a_mg_m3=self._safe_float(row.get('chlorophyll_a_mg_m3')),
                        nitrate_mg_l=self._safe_float(row.get('nitrate_mg_l')),
                        phosphate_mg_l=self._safe_float(row.get('phosphate_mg_l')),
                        turbidity_ntu=self._safe_float(row.get('turbidity_ntu')),
                        region=row.get('region'),
                        location_name=row.get('location_name'),
                        recorded_at=self._parse_datetime(row.get('recorded_at')),
                        data_source=f'Dataset_{dataset.id}',
                        quality_flag=row.get('quality_flag', 'good')
                    )
                    
                    db.session.add(ocean_data)
                    records_added += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing ocean data row: {e}")
                    continue
            
            db.session.commit()
            
            # Calculate quality metrics
            quality_score = self._calculate_data_quality(df)
            completeness = self._calculate_completeness(df)
            
            return {
                'success': True,
                'records_processed': records_added,
                'data_quality_score': quality_score,
                'completeness_percentage': completeness
            }
            
        except Exception as e:
            logger.error(f"Error processing ocean data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_edna_data(self, dataset, df):
        """Process eDNA dataset"""
        try:
            records_added = 0
            
            for _, row in df.iterrows():
                try:
                    # Check required fields
                    if pd.isna(row.get('sample_id')):
                        continue
                    
                    # Create eDNA sample record
                    edna_sample = EdnaSample(
                        dataset_id=dataset.id,
                        sample_id=row.get('sample_id'),
                        latitude=self._safe_float(row.get('latitude')),
                        longitude=self._safe_float(row.get('longitude')),
                        depth_m=self._safe_float(row.get('depth_m')),
                        collection_date=self._parse_date(row.get('collection_date')),
                        total_reads=self._safe_int(row.get('total_reads')),
                        quality_reads=self._safe_int(row.get('quality_reads')),
                        species_detected=self._safe_int(row.get('species_detected')),
                        shannon_diversity=self._safe_float(row.get('shannon_diversity')),
                        simpson_diversity=self._safe_float(row.get('simpson_diversity')),
                        processing_lab=row.get('processing_lab'),
                        sequencing_platform=row.get('sequencing_platform')
                    )
                    
                    db.session.add(edna_sample)
                    records_added += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing eDNA row: {e}")
                    continue
            
            db.session.commit()
            
            # Calculate quality metrics
            quality_score = self._calculate_data_quality(df)
            completeness = self._calculate_completeness(df)
            
            return {
                'success': True,
                'records_processed': records_added,
                'data_quality_score': quality_score,
                'completeness_percentage': completeness
            }
            
        except Exception as e:
            logger.error(f"Error processing eDNA data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_obis_data(self, dataset_id, obis_data):
        """Process OBIS API data"""
        try:
            dataset = Dataset.query.get(dataset_id)
            if not dataset:
                return {'success': False, 'error': 'Dataset not found'}
            
            records_added = 0
            
            for record in obis_data:
                try:
                    # Check if species exists, create if not
                    species = Species.query.filter_by(
                        scientific_name=record['scientific_name']
                    ).first()
                    
                    if not species:
                        species = Species(
                            dataset_id=dataset_id,
                            scientific_name=record['scientific_name'],
                            data_source='OBIS'
                        )
                        db.session.add(species)
                        db.session.flush() # Get ID
                    
                    # Create species occurrence record
                    occurrence = SpeciesOccurrence(
                        species_id=species.id,
                        dataset_id=dataset_id,
                        latitude=record['latitude'],
                        longitude=record['longitude'],
                        depth_m=record.get('depth_m'),
                        individual_count=record.get('individual_count'),
                        observed_at=self._parse_datetime(record.get('event_date')),
                        survey_method=record.get('basis_of_record', 'OBIS'),
                        observer=record.get('institution', 'OBIS'),
                        water_temperature_c=record.get('temperature_c'),
                        source_database='OBIS',
                        source_record_id=record.get('obis_id')
                    )
                    
                    db.session.add(occurrence)
                    records_added += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing OBIS record: {e}")
                    continue
            
            db.session.commit()
            
            return {
                'success': True,
                'records_processed': records_added,
                'data_quality_score': 0.9, # OBIS data is high quality
                'completeness_percentage': 85.0
            }
            
        except Exception as e:
            logger.error(f"Error processing OBIS data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_species_column_mapping(self):
        """Get column mapping for species data"""
        return {
            'scientific_name': ['scientific_name', 'scientificname', 'species', 'species_name', 'name'],
            'common_name': ['common_name', 'vernacular_name', 'commonname', 'popular_name'],
            'family': ['family'],
            'genus': ['genus'],
            'kingdom': ['kingdom'],
            'phylum': ['phylum'],
            'class': ['class', 'class_name'],
            'order': ['order', 'order_name'],
            'habitat': ['habitat', 'environment'],
            'conservation_status': ['conservation_status', 'iucn_status', 'status', 'redlist_status'],
            'commercial_importance': ['commercial_importance', 'commercial_value', 'fishery_importance'],
            'max_length_cm': ['max_length', 'length', 'max_size', 'size'],
            'trophic_level': ['trophic_level', 'trophic'],
            'description': ['description', 'notes', 'remarks']
        }
    
    def _get_ocean_column_mapping(self):
        """Get column mapping for oceanographic data"""
        return {
            'latitude': ['latitude', 'lat', 'y', 'coord_y'],
            'longitude': ['longitude', 'lon', 'lng', 'long', 'x', 'coord_x'],
            'depth_m': ['depth', 'depth_m', 'depth_meters', 'water_depth'],
            'temperature_c': ['temperature', 'temp', 'temperature_c', 'water_temp', 'sst'],
            'salinity_psu': ['salinity', 'sal', 'salinity_psu', 'sal_psu'],
            'ph_level': ['ph', 'ph_level', 'ph_value'],
            'dissolved_oxygen_ml_l': ['oxygen', 'do', 'dissolved_oxygen', 'o2'],
            'chlorophyll_a_mg_m3': ['chlorophyll', 'chl', 'chl_a', 'chlorophyll_a'],
            'region': ['region', 'area', 'location', 'site'],
            'recorded_at': ['date', 'time', 'datetime', 'timestamp', 'recorded_at', 'sample_date']
        }
    
    def _map_columns(self, df, column_mapping):
        """Map DataFrame columns to standardized names"""
        mapped_df = df.copy()
        columns_lower = {col: col.lower() for col in df.columns}
        
        for standard_name, possible_names in column_mapping.items():
            for possible_name in possible_names:
                matching_cols = [col for col_lower, col in columns_lower.items() 
                               if possible_name in col_lower]
                if matching_cols:
                    mapped_df[standard_name] = mapped_df[matching_cols[0]]
                    break
        
        return mapped_df
    
    def _safe_float(self, value):
        """Safely convert to float"""
        try:
            return float(value) if pd.notna(value) else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value):
        """Safely convert to int"""
        try:
            return int(value) if pd.notna(value) else None
        except (ValueError, TypeError):
            return None
    
    def _parse_datetime(self, date_str):
        """Parse various datetime formats"""
        if pd.isna(date_str):
            return datetime.now()
        
        try:
            return pd.to_datetime(date_str)
        except:
            return datetime.now()
    
    def _parse_date(self, date_str):
        """Parse date string"""
        try:
            return pd.to_datetime(date_str).date()
        except:
            return datetime.now().date()
    
    def _calculate_data_quality(self, df):
        """Calculate overall data quality score (0-1)"""
        total_cells = df.shape[0] * df.s