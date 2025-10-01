# Supabase Data Migration Guide

## Step 1: Tables Created ✅
You've already created the 4 tables in Supabase:
- `species`
- `oceanographic_data`
- `edna_samples`
- `datasets`

## Step 2: Data Migration Options

### Option A: Manual SQL Insert (Recommended)

Since API key authentication can be tricky, here's a manual approach using Supabase SQL Editor:

#### 1. Create Dataset Records First

Go to your Supabase SQL Editor and run these commands:

```sql
-- Insert dataset for species data
INSERT INTO datasets (name, dataset_type, source_type, original_filename, description, region, processed, data_quality_score, records_count)
VALUES ('Sample Species Data', 'Species', 'CSV Migration', 'sample-species-data.csv', 'Marine species data from sample CSV', 'Indian Ocean', true, 0.95, 10);

-- Insert dataset for ocean data
INSERT INTO datasets (name, dataset_type, source_type, original_filename, description, region, processed, data_quality_score, records_count)
VALUES ('Sample Ocean Data', 'Ocean', 'CSV Migration', 'sample-ocean-data.csv', 'Oceanographic data from sample CSV', 'Indian Ocean', true, 0.92, 15);

-- Insert dataset for eDNA data
INSERT INTO datasets (name, dataset_type, source_type, original_filename, description, region, processed, data_quality_score, records_count)
VALUES ('Sample eDNA Data', 'eDNA', 'CSV Migration', 'sample-edna-data.csv', 'Environmental DNA data from sample CSV', 'Indian Ocean', true, 0.88, 15);
```

#### 2. Get Dataset IDs

After inserting datasets, get their IDs:

```sql
SELECT id, name FROM datasets ORDER BY created_at DESC LIMIT 3;
```

Note down the IDs (let's assume they are 1, 2, 3 for species, ocean, eDNA respectively).

#### 3. Insert Species Data

```sql
INSERT INTO species (dataset_id, scientific_name, common_name, family, genus, order_name, class_name, phylum, kingdom, habitat, conservation_status, max_length_cm, trophic_level, depth_range_min_m, depth_range_max_m, temperature_range_min_c, temperature_range_max_c, commercial_importance, description, threats, geographic_distribution, data_source) VALUES
(1, 'Thunnus albacares', 'Yellowfin Tuna', 'Scombridae', 'Thunnus', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'pelagic', 'Near Threatened', 239, 4.3, 0, 250, 15, 31, 'High', 'Large pelagic fish found in tropical and subtropical oceans worldwide. Known for high-speed swimming and commercial value.', 'Overfishing, climate change, habitat degradation', 'Tropical and subtropical waters of Atlantic, Pacific, and Indian Oceans', 'CSV Migration'),
(1, 'Sardinella longiceps', 'Indian Oil Sardine', 'Clupeidae', 'Sardinella', 'Clupeiformes', 'Actinopterygii', 'Chordata', 'Animalia', 'coastal', 'Least Concern', 23, 3.1, 0, 200, 20, 30, 'High', 'Small pelagic fish forming large schools in coastal waters of the Indian Ocean.', 'Overfishing, pollution, coastal development', 'Arabian Sea, Bay of Bengal, coastal waters of India', 'CSV Migration'),
(1, 'Lutjanus campechanus', 'Red Snapper', 'Lutjanidae', 'Lutjanus', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'reef', 'Vulnerable', 100, 3.8, 10, 190, 18, 28, 'High', 'Commercially important reef fish with distinctive red coloration.', 'Overfishing, habitat destruction, climate change', 'Gulf of Mexico, Caribbean, Western Atlantic', 'CSV Migration'),
(1, 'Epinephelus marginatus', 'Dusky Grouper', 'Serranidae', 'Epinephelus', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'reef', 'Endangered', 150, 4.2, 20, 200, 14, 26, 'High', 'Large predatory fish inhabiting rocky reefs and coastal areas.', 'Overfishing, habitat loss, slow reproduction', 'Mediterranean Sea, Eastern Atlantic', 'CSV Migration'),
(1, 'Rastrelliger kanagurta', 'Indian Mackerel', 'Scombridae', 'Rastrelliger', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'coastal', 'Least Concern', 35, 3.5, 0, 100, 22, 30, 'High', 'Commercially important small pelagic fish in Indo-Pacific waters.', 'Overfishing, climate variability', 'Indo-Pacific, Arabian Sea, Bay of Bengal', 'CSV Migration'),
(1, 'Katsuwonus pelamis', 'Skipjack Tuna', 'Scombridae', 'Katsuwonus', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'pelagic', 'Least Concern', 108, 4.1, 0, 260, 15, 30, 'High', 'Highly migratory tuna species with global distribution.', 'Climate change, overfishing in some regions', 'All tropical and subtropical oceans', 'CSV Migration'),
(1, 'Pristis pristis', 'Common Sawfish', 'Pristidae', 'Pristis', 'Pristiformes', 'Chondrichthyes', 'Chordata', 'Animalia', 'coastal', 'Critically Endangered', 760, 4.5, 0, 122, 20, 30, 'Low', 'Large ray with distinctive saw-like rostrum, critically endangered.', 'Habitat loss, fishing pressure, climate change', 'Historically tropical/subtropical coasts, now severely reduced', 'CSV Migration'),
(1, 'Chelonia mydas', 'Green Turtle', 'Cheloniidae', 'Chelonia', 'Testudines', 'Reptilia', 'Chordata', 'Animalia', 'marine', 'Endangered', 153, 2.8, 0, 110, 20, 35, 'Low', 'Large sea turtle, herbivorous as adult, globally distributed.', 'Plastic pollution, fishing gear, habitat loss, climate change', 'Tropical and subtropical oceans worldwide', 'CSV Migration'),
(1, 'Carcharinus amblyrhynchos', 'Grey Reef Shark', 'Carcharhinidae', 'Carcharinus', 'Carcharhiniformes', 'Chondrichthyes', 'Chordata', 'Animalia', 'reef', 'Near Threatened', 255, 4.8, 0, 280, 22, 30, 'Medium', 'Reef-associated shark species important for ecosystem health.', 'Overfishing, habitat degradation, shark finning', 'Indo-Pacific coral reefs', 'CSV Migration'),
(1, 'Euthynnus affinis', 'Kawakawa', 'Scombridae', 'Euthynnus', 'Perciformes', 'Actinopterygii', 'Chordata', 'Animalia', 'coastal', 'Least Concern', 100, 3.9, 0, 200, 20, 30, 'Medium', 'Small tuna species common in Indo-Pacific coastal waters.', 'Overfishing, habitat changes', 'Indo-Pacific, Red Sea to Australia', 'CSV Migration');
```

### Option B: Use Supabase Dashboard Import

1. Go to your Supabase dashboard
2. Navigate to Table Editor
3. Select each table (species, oceanographic_data, edna_samples)
4. Click "Insert" → "Import data from CSV"
5. Upload your CSV files directly

### Option C: Fix API Key and Use Python Script

If you want to use the Python script:

1. Go to your Supabase dashboard
2. Navigate to Settings → API
3. Copy your **service_role** key (not anon key)
4. Replace the key in the migration script
5. Run the script again

## Step 3: Verify Data Migration

After migration, verify your data:

```sql
-- Check datasets
SELECT * FROM datasets;

-- Check species count
SELECT COUNT(*) as species_count FROM species;

-- Check ocean data count
SELECT COUNT(*) as ocean_records FROM oceanographic_data;

-- Check eDNA data count
SELECT COUNT(*) as edna_samples FROM edna_samples;

-- Sample queries to test data
SELECT scientific_name, common_name, conservation_status FROM species LIMIT 5;
SELECT latitude, longitude, temperature_c, salinity_psu FROM oceanographic_data LIMIT 5;
SELECT sample_id, species_detected, shannon_diversity FROM edna_samples LIMIT 5;
```

## Step 4: Update Your Application

Once data is migrated, your Flask application should be able to connect to Supabase and display the data. The connection is already configured in your `config.py` file.

## Next Steps

1. **Test your application**: Run your Flask app and verify it can read data from Supabase
2. **Add more data**: You can add more CSV files or connect to external APIs
3. **Set up real-time features**: Use Supabase's real-time capabilities
4. **Add authentication**: Implement user authentication with Supabase Auth
5. **File storage**: Use Supabase Storage for images and documents

## Troubleshooting

- **Connection issues**: Check your database URL and API keys
- **Permission errors**: Make sure you're using the correct API key with proper permissions
- **Data type errors**: Ensure CSV data matches the table schema
- **Large datasets**: For large files, consider batch processing or using Supabase's bulk import features

Your Supabase database is now ready to power your Marine Biodiversity Platform! 🌊🐟