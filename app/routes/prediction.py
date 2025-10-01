
from flask import request
from flask_restx import Namespace, Resource
from ..services.prediction_service import PredictionService

prediction_ns = Namespace('predict', description='Species distribution prediction')

@prediction_ns.route('/species/<int:species_id>')
class SpeciesPrediction(Resource):
    def post(self, species_id):
        """Predict the probability of species presence at a given location."""
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        month = data.get('month')

        if not all([latitude, longitude, month]):
            return {'message': 'Missing required parameters: latitude, longitude, month'}, 400

        try:
            service = PredictionService(species_id)
            service.train_model()
            probability = service.predict(latitude, longitude, month)
            return {'species_id': species_id, 'probability_of_presence': probability}
        except Exception as e:
            return {'message': f'Error making prediction: {str(e)}'}, 500
