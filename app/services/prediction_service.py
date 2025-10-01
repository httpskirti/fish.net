
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
from ..models import db, Species, SpeciesOccurrence, OceanographicData

class PredictionService:
    def __init__(self, species_id):
        self.species_id = species_id
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def _get_data(self):
        occurrences = SpeciesOccurrence.query.filter_by(species_id=self.species_id).all()
        occurrence_data = [
            {
                'latitude': o.latitude,
                'longitude': o.longitude,
                'month': o.observed_at.month
            } for o in occurrences
        ]
        occurrence_df = pd.DataFrame(occurrence_data)

        ocean_data = OceanographicData.query.all()
        ocean_df = pd.DataFrame([o.to_dict() for o in ocean_data])

        # For simplicity, we'll merge based on the closest location and month.
        # This is a simplification and a more robust solution would be needed for a real application.
        merged_df = pd.merge(occurrence_df, ocean_df, on=['latitude', 'longitude', 'month'], how='inner')
        return merged_df

    def train_model(self):
        data = self._get_data()
        if data.empty:
            return

        X = data[['latitude', 'longitude', 'sea_surface_temp', 'salinity', 'current_speed']]
        y = data['species_id'] 

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy}")


    def predict(self, latitude, longitude, month):
        # In a real application, you would fetch the oceanographic data for the given location and month
        # For now, we'll use some dummy data.
        dummy_ocean_data = {
            'sea_surface_temp': 25.0,
            'salinity': 35.0,
            'current_speed': 0.5
        }
        
        df = pd.DataFrame({
            'latitude': [latitude],
            'longitude': [longitude],
            'sea_surface_temp': [dummy_ocean_data['sea_surface_temp']],
            'salinity': [dummy_ocean_data['salinity']],
            'current_speed': [dummy_ocean_data['current_speed']]
        })
        
        prediction = self.model.predict_proba(df)
        return prediction[0][1] # Probability of presence
