"""

OBIS (Ocean Biodiversity Information System) Integration Service
Connects to real OBIS API for marine species data
"""
import requests
import json
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class OBISIntegration:
    """
    Integration with OBIS API for real marine biodiversity data
    """
    
    def __init__(self):
        self.base_url = "https://api.obis.org/v3"
        self.headers = {
            'User-Agent': 'Marine-Biodiversity-Platform/1.0',
            'Accept': 'application/json'
        }
        
    def fetch_species_occurrences(self, region='Indian Ocean', geometry=None, limit=1000):
        """
        Fetch species occurrence data from OBIS
        
        Args:
            region: Geographic region name
            geometry: Optional geometry filter (WKT or GeoJSON)
            limit: Maximum number of records to fetch
            
        Returns:
            Dictionary with success status and data
        """
        try:
            logger.info(f"Fetching OBIS data for region: {region}")
            
            # OBIS API parameters
            params = {
                'limit': min(limit, 5000), # OBIS limit
                'offset': 0,
                'fields': 'scientificName,decimalLatitude,decimalLongitude,eventDate,individualCount,occurrenceStatus,basisOfRecord,datasetName,institutionCode,country,locality,depth,temperature,salinity'
            }
            
            # Add geometry filter for Indian Ocean if no specific geometry provided
            if not geometry:
                # Approximate Indian Ocean bounding box
                indian_ocean_bbox = "POLYGON((20 -50, 20 30, 120 30, 120 -50, 20 -50))"
                params['geometry'] = indian_ocean_bbox
            else:
                params['geometry'] = geometry
                
            # Add text search for region if specified
            if region and region != 'Indian Ocean':
                params['locality'] = region
            
            # Make API request
            url = f"{self.base_url}/occurrence"
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the results
                occurrences = data.get('results', [])
                logger.info(f"Retrieved {len(occurrences)} occurrence records from OBIS")
                
                # Clean and standardize the data
                cleaned_data = self._clean_obis_data(occurrences)
                
                return {
                    'success': True,
                    'data': cleaned_data,
                    'records_count': len(cleaned_data),
                    'total_available': data.get('count', len(cleaned_data)),
                    'source': 'OBIS',
                    'api_response_time': response.elapsed.total_seconds()
                }
            else:
                logger.error(f"OBIS API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"OBIS API returned status {response.status_code}",
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error accessing OBIS API: {str(e)}")
            return {
                'success': False,
                'error': 'Network error accessing OBIS API',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in OBIS integration: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error in OBIS integration',
                'details': str(e)
            }
    
    def _clean_obis_data(self, raw_data):
        """
        Clean and standardize OBIS data
        
        Args:
            raw_data: Raw data from OBIS API
            
        Returns:
            List of cleaned occurrence records
        """
        cleaned_records = []
        
        for record in raw_data:
            try:
                # Skip records without essential data
                if not all([
                    record.get('scientificName'),
                    record.get('decimalLatitude'),
                    record.get('decimalLongitude')
                ]):
                    continue
                
                cleaned_record = {
                    'scientific_name': record.get('scientificName', '').strip(),
                    'latitude': float(record.get('decimalLatitude')),
                    'longitude': float(record.get('decimalLongitude')),
                    'event_date': record.get('eventDate'),
                    'individual_count': record.get('individualCount'),
                    'occurrence_status': record.get('occurrenceStatus', 'present'),
                    'basis_of_record': record.get('basisOfRecord'),
                    'dataset_name': record.get('datasetName'),
                    'institution': record.get('institutionCode'),
                    'country': record.get('country'),
                    'locality': record.get('locality'),
                    'depth_m': self._safe_float(record.get('depth')),
                    'temperature_c': self._safe_float(record.get('temperature')),
                    'salinity_psu': self._safe_float(record.get('salinity')),
                    'obis_id': record.get('id'),
                    'source': 'OBIS'
                }
                
                cleaned_records.append(cleaned_record)
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed OBIS record: {e}")
                continue
        
        logger.info(f"Cleaned {len(cleaned_records)} valid records from {len(raw_data)} raw records")
        return cleaned_records
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def fetch_species_info(self, scientific_name):
        """
        Fetch detailed species information from OBIS
        
        Args:
            scientific_name: Scientific name of the species
            
        Returns:
            Dictionary with species information
        """
        try:
            params = {
                'scientificname': scientific_name,
                'fields': 'AphiaID,scientificName,authority,status,rank,kingdom,phylum,class,order,family,genus,species'
            }
            
            url = f"{self.base_url}/taxon"
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    return {
                        'success': True,
                        'species_info': results[0],
                        'source': 'OBIS'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No species information found for {scientific_name}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'OBIS species API returned status {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error fetching species info from OBIS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_regional_statistics(self, region='Indian Ocean'):
        """
        Get regional biodiversity statistics from OBIS
        
        Args:
            region: Geographic region
            
        Returns:
            Dictionary with regional statistics
        """
        try:
            # Get statistics for the region
            params = {
                'geometry': "POLYGON((20 -50, 20 30, 120 30, 120 -50, 20 -50))" if region == 'Indian Ocean' else None,
                'locality': region if region != 'Indian Ocean' else None
            }
            
            stats_url = f"{self.base_url}/statistics"
            response = requests.get(stats_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'statistics': data,
                    'source': 'OBIS'
                }
            else:
                return {
                    'success': False,
                    'error': f'OBIS statistics API returned status {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error fetching regional statistics from OBIS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def test_connection(self):
        """
        Test connection to OBIS API
        
        Returns:
            Dictionary with connection status
        """
        try:
            url = f"{self.base_url}/occurrence"
            params = {'limit': 1}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status': 'Connected to OBIS API',
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    'success': False,
                    'error': f'OBIS API connection failed with status {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Cannot connect to OBIS API: {str(e)}'
            }