"""
AI Service for Species Identification using Google Gemini API
"""
import requests
import base64
import json
from typing import Dict, List, Optional
import os

class AIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or 'AIzaSyBqrpEqa8dcN-LGm74cPdwyTjGrvn8sv0Y'
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'
    
    def identify_species_from_image(self, image_data: bytes, filename: str = None) -> Dict:
        """
        Identify marine species from an uploaded image using Gemini Vision API
        """
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": """Analyze this image and identify any marine species present. 
                            Please provide:
                            1. Scientific name of the species
                            2. Common name
                            3. Family classification
                            4. Confidence level (0-100%)
                            5. Key identifying features visible in the image
                            6. Habitat information
                            7. Conservation status if known
                            
                            Format your response as JSON with the following structure:
                            {
                                "species_identified": [
                                    {
                                        "scientific_name": "",
                                        "common_name": "",
                                        "family": "",
                                        "confidence": 0,
                                        "identifying_features": [],
                                        "habitat": "",
                                        "conservation_status": ""
                                    }
                                ],
                                "image_quality": "",
                                "analysis_notes": ""
                            }"""
                        },
                        {
                            "inline_data": {
                                "mime_type": self._get_mime_type(filename),
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated text
                if 'candidates' in result and len(result['candidates']) > 0:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Try to parse JSON from the response
                    try:
                        # Clean the response text to extract JSON
                        json_start = generated_text.find('{')
                        json_end = generated_text.rfind('}') + 1
                        
                        if json_start != -1 and json_end != -1:
                            json_text = generated_text[json_start:json_end]
                            parsed_result = json.loads(json_text)
                            return {
                                'success': True,
                                'data': parsed_result,
                                'raw_response': generated_text
                            }
                        else:
                            # Fallback: create structured response from text
                            return self._parse_text_response(generated_text)
                    
                    except json.JSONDecodeError:
                        # Fallback: create structured response from text
                        return self._parse_text_response(generated_text)
                
                else:
                    return {
                        'success': False,
                        'error': 'No response generated from AI model'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code} - {response.text}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in species identification: {str(e)}'
            }
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        if not filename:
            return 'image/jpeg'
        
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response when JSON parsing fails"""
        try:
            # Create a basic structured response from the text
            species_data = {
                'scientific_name': 'Unknown',
                'common_name': 'Unknown',
                'family': 'Unknown',
                'confidence': 50,
                'identifying_features': [],
                'habitat': 'Marine environment',
                'conservation_status': 'Unknown'
            }
            
            # Try to extract key information from text
            lines = text.split('\n')
            for line in lines:
                line = line.strip().lower()
                if 'scientific name' in line or 'species:' in line:
                    # Extract species name
                    parts = line.split(':')
                    if len(parts) > 1:
                        species_data['scientific_name'] = parts[1].strip().title()
                
                elif 'common name' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        species_data['common_name'] = parts[1].strip().title()
                
                elif 'family' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        species_data['family'] = parts[1].strip().title()
            
            return {
                'success': True,
                'data': {
                    'species_identified': [species_data],
                    'image_quality': 'Analyzed',
                    'analysis_notes': text
                },
                'raw_response': text
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error parsing response: {str(e)}'
            }
    
    def get_species_information(self, scientific_name: str) -> Dict:
        """
        Get detailed information about a species using Gemini API
        """
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""Provide detailed information about the marine species: {scientific_name}
                        
                        Please include:
                        1. Scientific classification (Kingdom, Phylum, Class, Order, Family, Genus, Species)
                        2. Common names
                        3. Physical description and size
                        4. Habitat and distribution
                        5. Diet and behavior
                        6. Conservation status
                        7. Commercial importance
                        8. Interesting facts
                        
                        Format as JSON:
                        {{
                            "scientific_name": "",
                            "common_names": [],
                            "classification": {{}},
                            "physical_description": "",
                            "size_range": "",
                            "habitat": "",
                            "distribution": "",
                            "diet": "",
                            "behavior": "",
                            "conservation_status": "",
                            "commercial_importance": "",
                            "interesting_facts": []
                        }}"""
                    }]
                }]
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    try:
                        # Extract JSON from response
                        json_start = generated_text.find('{')
                        json_end = generated_text.rfind('}') + 1
                        
                        if json_start != -1 and json_end != -1:
                            json_text = generated_text[json_start:json_end]
                            parsed_result = json.loads(json_text)
                            return {
                                'success': True,
                                'data': parsed_result
                            }
                    
                    except json.JSONDecodeError:
                        pass
                    
                    return {
                        'success': True,
                        'data': {'description': generated_text}
                    }
            
            return {
                'success': False,
                'error': 'Failed to get species information'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting species information: {str(e)}'
            }