"""
Marine Biodiversity Platform - Database Models
Designed to handle real oceanographic and species data
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Dataset(db.Model):
    """Track all uploaded and connected datasets"""
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dataset_type = db.Column(db.String(50))  # Species, Ocean, eDNA, Routes, etc.
    source_type = db.Column(db.String(50))   # Upload, OBIS, API, etc.
    
    # File information
    original_filename = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    file_size_mb = db.Column(db.Float)
    
    # Dataset metadata
    description = db.Column(db.Text)
    region = db.Column(db.String(100))
    collection_start_date = db.Column(db.Date)
    collection_end_date = db.Column(db.Date)
    data_source_organization = db.Column(db.String(200))
    
    # Processing status
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_errors = db.Column(db.Text)
    records_count = db.Column(db.Integer, default=0)
    
    # Data quality metrics
    data_quality_score = db.Column(db.Float)  # 0-1 scale
    completeness_percentage = db.Column(db.Float)
    
    # API connection info
    api_endpoint = db.Column(db.String(500))
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dataset_type': self.dataset_type,
            'source_type': self.source_type,
            'description': self.description,
            'region': self.region,
            'records_count': self.records_count,
            'file_size_mb': self.file_size_mb,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed': self.processed,
            'data_quality_score': self.data_quality_score,
            'completeness_percentage': self.completeness_percentage,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

class Species(db.Model):
    """Comprehensive species information from multiple sources"""
    __tablename__ = 'species'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    
    # Taxonomic information
    scientific_name = db.Column(db.String(150), nullable=False, index=True)
    common_name = db.Column(db.String(150))
    kingdom = db.Column(db.String(50), default='Animalia')
    phylum = db.Column(db.String(50))
    class_name = db.Column(db.String(50))
    order = db.Column(db.String(50))
    family = db.Column(db.String(50), index=True)
    genus = db.Column(db.String(50))
    species = db.Column(db.String(50))
    
    # Physical characteristics
    max_length_cm = db.Column(db.Float)
    max_weight_kg = db.Column(db.Float)
    average_lifespan_years = db.Column(db.Integer)
    body_shape = db.Column(db.String(100))
    
    # Ecological information
    habitat = db.Column(db.String(100))
    diet = db.Column(db.String(200))
    trophic_level = db.Column(db.Float)
    feeding_behavior = db.Column(db.String(100))
    reproduction_type = db.Column(db.String(100))
    
    # Conservation status
    conservation_status = db.Column(db.String(50), index=True)
    population_trend = db.Column(db.String(50))
    threats = db.Column(db.Text)
    protection_status = db.Column(db.String(100))
    
    # Commercial information
    commercial_importance = db.Column(db.String(20))
    fishing_methods = db.Column(db.Text)
    market_value_usd_kg = db.Column(db.Float)
    fishery_status = db.Column(db.String(50))
    
    # Distribution
    endemic_to_indian_ocean = db.Column(db.Boolean, default=False)
    depth_range_min_m = db.Column(db.Float)
    depth_range_max_m = db.Column(db.Float)
    temperature_range_min_c = db.Column(db.Float)
    temperature_range_max_c = db.Column(db.Float)
    salinity_tolerance = db.Column(db.String(50))
    geographic_distribution = db.Column(db.Text)
    
    # Visual and identification
    image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    identification_features = db.Column(db.Text)
    similar_species = db.Column(db.Text)
    
    # Data source tracking
    data_source = db.Column(db.String(100))
    source_id = db.Column(db.String(100))  # Original ID from source database
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = db.relationship('Dataset', backref='species_data')
    occurrences = db.relationship('SpeciesOccurrence', backref='species_info', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'scientific_name': self.scientific_name,
            'common_name': self.common_name,
            'family': self.family,
            'habitat': self.habitat,
            'conservation_status': self.conservation_status,
            'commercial_importance': self.commercial_importance,
            'max_length_cm': self.max_length_cm,
            'trophic_level': self.trophic_level,
            'image_url': self.image_url,
            'description': self.description,
            'threats': self.threats,
            'population_trend': self.population_trend,
            'geographic_distribution': self.geographic_distribution
        }

class OceanographicData(db.Model):
    """Real oceanographic measurements"""
    __tablename__ = 'oceanographic_data'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    
    # Location
    latitude = db.Column(db.Float, nullable=False, index=True)
    longitude = db.Column(db.Float, nullable=False, index=True)
    location_name = db.Column(db.String(100))
    region = db.Column(db.String(100), index=True)
    country = db.Column(db.String(100))
    
    # Physical parameters
    depth_m = db.Column(db.Float, index=True)
    temperature_c = db.Column(db.Float, index=True)
    salinity_psu = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    dissolved_oxygen_ml_l = db.Column(db.Float)
    turbidity_ntu = db.Column(db.Float)
    conductivity = db.Column(db.Float)
    
    # Chemical parameters
    nitrate_mg_l = db.Column(db.Float)
    phosphate_mg_l = db.Column(db.Float)
    silicate_mg_l = db.Column(db.Float)
    chlorophyll_a_mg_m3 = db.Column(db.Float)
    total_nitrogen = db.Column(db.Float)
    total_phosphorus = db.Column(db.Float)
    
    # Biological indicators
    primary_productivity = db.Column(db.Float)
    bacterial_count = db.Column(db.Integer)
    phytoplankton_abundance = db.Column(db.Float)
    zooplankton_abundance = db.Column(db.Float)
    
    # Environmental conditions
    water_current_speed_ms = db.Column(db.Float)
    water_current_direction = db.Column(db.Float)
    wave_height_m = db.Column(db.Float)
    wind_speed_ms = db.Column(db.Float)
    wind_direction = db.Column(db.Float)
    
    # Data collection metadata
    recorded_at = db.Column(db.DateTime, nullable=False, index=True)
    measurement_depth_m = db.Column(db.Float)
    sampling_method = db.Column(db.String(100))
    instrument_type = db.Column(db.String(100))
    data_source = db.Column(db.String(100))
    quality_flag = db.Column(db.String(20), default='good')
    
    # Weather at time of measurement
    air_temperature_c = db.Column(db.Float)
    weather_conditions = db.Column(db.String(100))
    sea_state = db.Column(db.String(50))
    visibility_km = db.Column(db.Float)
    
    # Relationships
    dataset = db.relationship('Dataset', backref='ocean_data')
    
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'region': self.region,
            'depth_m': self.depth_m,
            'temperature_c': self.temperature_c,
            'salinity_psu': self.salinity_psu,
            'ph_level': self.ph_level,
            'dissolved_oxygen_ml_l': self.dissolved_oxygen_ml_l,
            'chlorophyll_a_mg_m3': self.chlorophyll_a_mg_m3,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'data_source': self.data_source,
            'quality_flag': self.quality_flag
        }

class SpeciesOccurrence(db.Model):
    """Species observation and catch records"""
    __tablename__ = 'species_occurrence'
    
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False, index=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth_m = db.Column(db.Float)
    location_accuracy_m = db.Column(db.Float)
    
    # Observation data
    abundance = db.Column(db.Integer)
    biomass_kg = db.Column(db.Float)
    individual_count = db.Column(db.Integer)
    size_range_cm = db.Column(db.String(50))
    average_length_cm = db.Column(db.Float)
    average_weight_g = db.Column(db.Float)
    life_stage = db.Column(db.String(50))
    sex = db.Column(db.String(20))
    
    # Collection details
    observed_at = db.Column(db.DateTime, nullable=False, index=True)
    observer = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    survey_method = db.Column(db.String(100))
    sampling_effort = db.Column(db.String(200))
    gear_type = db.Column(db.String(100))
    
    # Environmental context
    water_temperature_c = db.Column(db.Float)
    water_depth_m = db.Column(db.Float)
    salinity_psu = db.Column(db.Float)
    
    # Data quality
    identification_confidence = db.Column(db.String(20))
    verified_by = db.Column(db.String(100))
    verification_status = db.Column(db.String(20))
    notes = db.Column(db.Text)
    
    # Source tracking
    source_database = db.Column(db.String(100))
    source_record_id = db.Column(db.String(100))
    
    # Relationships
    dataset = db.relationship('Dataset', backref='species_occurrences')
    
    def to_dict(self):
        return {
            'id': self.id,
            'species_id': self.species_id,
            'scientific_name': self.species_info.scientific_name if self.species_info else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'abundance': self.abundance,
            'biomass_kg': self.biomass_kg,
            'observed_at': self.observed_at.isoformat() if self.observed_at else None,
            'survey_method': self.survey_method,
            'observer': self.observer,
            'identification_confidence': self.identification_confidence
        }

class SeaRoute(db.Model):
    """Maritime routes and shipping lanes"""
    __tablename__ = 'sea_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    
    # Route information
    route_name = db.Column(db.String(200), nullable=False)
    route_code = db.Column(db.String(50))
    route_type = db.Column(db.String(50))  # Commercial, Fishing, Historical, Military
    route_status = db.Column(db.String(50))  # Active, Historical, Seasonal
    
    # Geographic data
    start_port = db.Column(db.String(100))
    end_port = db.Column(db.String(100))
    intermediate_ports = db.Column(db.Text)  # JSON array
    coordinates_json = db.Column(db.Text)  # GeoJSON LineString
    total_distance_km = db.Column(db.Float)
    
    # Route characteristics
    traffic_density = db.Column(db.String(20))  # Low, Medium, High, Very High
    vessel_types = db.Column(db.String(200))  # Container, Tanker, Bulk, etc.
    seasonal_usage = db.Column(db.String(200))
    
    # Environmental impact
    environmental_risk = db.Column(db.String(20))  # Low, Medium, High
    protected_areas_crossed = db.Column(db.Text)
    sensitive_ecosystems = db.Column(db.Text)
    
    # Regulatory information
    maritime_authority = db.Column(db.String(100))
    restrictions = db.Column(db.Text)
    required_permits = db.Column(db.Text)
    
    # Data source
    data_source = db.Column(db.String(100))
    source_url = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = db.relationship('Dataset', backref='sea_routes')
    
    def get_coordinates(self):
        if self.coordinates_json:
            return json.loads(self.coordinates_json)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'route_name': self.route_name,
            'route_type': self.route_type,
            'start_port': self.start_port,
            'end_port': self.end_port,
            'coordinates': self.get_coordinates(),
            'traffic_density': self.traffic_density,
            'environmental_risk': self.environmental_risk,
            'total_distance_km': self.total_distance_km
        }

class EdnaSample(db.Model):
    """Environmental DNA sample analysis"""
    __tablename__ = 'edna_samples'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
    
    # Sample identification
    sample_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    field_sample_id = db.Column(db.String(50))
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth_m = db.Column(db.Float)
    location_description = db.Column(db.String(200))
    
    # Sample collection
    collection_date = db.Column(db.Date, nullable=False)
    collection_time = db.Column(db.Time)
    collector = db.Column(db.String(100))
    collection_method = db.Column(db.String(100))
    sample_volume_l = db.Column(db.Float)
    filtration_method = db.Column(db.String(100))
    filter_type = db.Column(db.String(50))
    filter_pore_size_um = db.Column(db.Float)
    
    # Laboratory processing
    processing_lab = db.Column(db.String(100))
    extraction_date = db.Column(db.Date)
    extraction_method = db.Column(db.String(100))
    pcr_primers = db.Column(db.String(200))
    sequencing_platform = db.Column(db.String(100))
    library_prep_method = db.Column(db.String(100))
    
    # Sequencing results
    total_reads = db.Column(db.Integer)
    quality_reads = db.Column(db.Integer)
    unique_sequences = db.Column(db.Integer)
    species_detected = db.Column(db.Integer)
    
    # Biodiversity metrics
    shannon_diversity = db.Column(db.Float)
    simpson_diversity = db.Column(db.Float)
    species_richness = db.Column(db.Integer)
    evenness_index = db.Column(db.Float)
    
    # Results data (JSON)
    detected_species_json = db.Column(db.Text)  # Detailed species list
    sequence_data_json = db.Column(db.Text)     # Raw sequence information
    taxonomy_summary_json = db.Column(db.Text)   # Taxonomic breakdown
    
    # Environmental context
    water_temperature_c = db.Column(db.Float)
    salinity_psu = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    dissolved_oxygen_ml_l = db.Column(db.Float)
    turbidity_ntu = db.Column(db.Float)
    
    # Quality control
    negative_control = db.Column(db.Boolean, default=False)
    positive_control = db.Column(db.Boolean, default=False)
    extraction_blank = db.Column(db.Boolean, default=False)
    pcr_blank = db.Column(db.Boolean, default=False)
    contamination_check = db.Column(db.String(50))
    quality_score = db.Column(db.Float)
    
    # Relationships  
    dataset = db.relationship('Dataset', backref='edna_samples')
    
    def get_detected_species(self):
        if self.detected_species_json:
            return json.loads(self.detected_species_json)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'sample_id': self.sample_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'species_detected': self.species_detected,
            'shannon_diversity': self.shannon_diversity,
            'detected_species': self.get_detected_species(),
            'processing_lab': self.processing_lab,
            'total_reads': self.total_reads
        }