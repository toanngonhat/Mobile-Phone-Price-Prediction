"""Prediction service for mobile phone price prediction"""
from app.services.model_loader import ModelLoader
from app.models.phone_features import PhoneFeatures
from app.utils.data_utils import prepare_features


class PredictionService:
    """Service for handling price predictions"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the prediction model"""
        try:
            self.model = self.model_loader.load_model()
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            self.model = None
    
    def predict(self, features: PhoneFeatures) -> float:
        """
        Predict phone price based on features
        
        Args:
            features: PhoneFeatures object containing phone specifications
            
        Returns:
            Predicted price as float
        """
        # Prepare features for model
        feature_array = prepare_features(features)
        
        # If model is not loaded, use a simple heuristic
        if self.model is None:
            return self._heuristic_prediction(features)
        
        # Use the loaded model for prediction
        prediction = self.model.predict([feature_array])
        return float(prediction[0])
    
    def _heuristic_prediction(self, features: PhoneFeatures) -> float:
        """
        Simple heuristic for price prediction when model is not available
        
        Args:
            features: PhoneFeatures object
            
        Returns:
            Estimated price
        """
        # Simple weighted sum based on key features
        base_price = 100.0
        
        # RAM contribution
        base_price += features.ram * 0.2
        
        # Storage contribution
        base_price += features.int_memory * 5.0
        
        # Battery contribution
        base_price += features.battery_power * 0.05
        
        # Camera contribution
        base_price += features.pc * 10.0
        base_price += features.fc * 5.0
        
        # Connectivity features
        if features.four_g:
            base_price += 50.0
        if features.three_g:
            base_price += 20.0
        if features.wifi:
            base_price += 15.0
        
        # Screen size contribution
        screen_area = features.sc_h * features.sc_w
        base_price += screen_area * 2.0
        
        return round(base_price, 2)
