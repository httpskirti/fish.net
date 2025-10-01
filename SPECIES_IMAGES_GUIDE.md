# Species Images Guide

## How to Add Species Images

To add images for species in the FishNet platform, follow these steps:

### 1. Image Requirements
- **Format**: JPG, JPEG, PNG
- **Size**: Recommended 800x600 pixels or higher
- **Quality**: High resolution, clear images showing key identifying features
- **File size**: Under 2MB per image

### 2. Naming Convention
Images should be named using the scientific name of the species, with spaces replaced by underscores and all lowercase:

**Examples:**
- `Thunnus albacares` → `thunnus_albacares.jpg`
- `Sardinella longiceps` → `sardinella_longiceps.jpg`
- `Lutjanus campechanus` → `lutjanus_campechanus.jpg`

### 3. File Location
Place all species images in the following directory:
```
c:\marine-biodiversity-platform\backend\app\static\images\species\
```

### 4. Current Species in Dataset
Based on your sample-species-data.csv, you can add images for these species:

1. **thunnus_albacares.jpg** - Yellowfin Tuna
2. **6** - Indian Oil Sardine
3. **lutjanus_campechanus.jpg** - Red Snapper
4. **epinephelus_marginatus.jpg** - Dusky Grouper
5. **rastrelliger_kanagurta.jpg** - Indian Mackerel
6. **katsuwonus_pelamis.jpg** - Skipjack Tuna
7. **pristis_pristis.jpg** - Common Sawfish
8. **chelonia_mydas.jpg** - Green Turtle
9. **carcharinus_amblyrhynchos.jpg** - Grey Reef Shark
10. **euthynnus_affinis.jpg** - Kawakawa

### 5. How Images Are Used
- **Species List Page**: Images appear as thumbnails in the species grid
- **Species Detail Modal**: Full-size images are displayed when clicking on a species
- **AI Identification**: Images can be used for training and comparison

### 6. Automatic Detection
The system automatically checks for images using the naming convention. If an image exists, it will be displayed. If not, a default fish icon placeholder is shown.

### 7. Adding New Species Images
When you add new species to your CSV data:
1. Follow the naming convention above
2. Place the image in the species folder
3. Refresh the species page to see the new image

### 8. Image Sources
Recommended sources for marine species images:
- **FishBase** (www.fishbase.org) - Scientific database with species photos
- **Encyclopedia of Life** (eol.org) - Open access biodiversity images
- **iNaturalist** - Community-contributed species photos
- **NOAA Fisheries** - Government marine species database
- **Marine Species Identification Portal** - Scientific identification guides

### 9. Copyright and Attribution
- Ensure you have rights to use the images
- Prefer Creative Commons or public domain images
- Keep attribution information if required
- For commercial use, verify licensing terms

### 10. Testing
After adding images:
1. Start the server: `python backend/run.py`
2. Visit: `http://localhost:5000/species`
3. Check that images load correctly
4. Click on species to see detail modal with full image

## Example Directory Structure
```
backend/app/static/images/species/
├── thunnus_albacares.jpg
├── sardinella_longiceps.jpg
├── lutjanus_campechanus.jpg
├── epinephelus_marginatus.jpg
├── rastrelliger_kanagurta.jpg
├── katsuwonus_pelamis.jpg
├── pristis_pristis.jpg
├── chelonia_mydas.jpg
├── carcharinus_amblyrhynchos.jpg
└── euthynnus_affinis.jpg
```

The system will automatically detect and display these images when you visit the species page!