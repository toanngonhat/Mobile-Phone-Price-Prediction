"""
Prediction service for mobile phone price estimation.
Coordinates between model loader and feature processing.
"""
from app.models.phone_features import PhoneFeatures
from app.services.model_loader import load_model


def predict_price(phone_features: PhoneFeatures) -> float:
    """
    Predict phone price based on input features.
    Currently uses mock model - will be replaced with trained ML model.
    
    TODO: Replace mock prediction with actual model inference
    TODO: Add feature preprocessing pipeline
    TODO: Handle model versioning
    """
    # Load model (currently returns mock model)
    model = load_model()
    
    # Prepare features for prediction
    features_dict = phone_features.model_dump()
    
    # Mock prediction logic - replace with actual model.predict()
    # This is a simple heuristic for demonstration
    base_price = 100
    
    # Brand factor (simplified)
    brand_multiplier = {
        "apple": 2.5,
        "samsung": 2.0,
        "google": 2.2,
        "xiaomi": 1.3,
        "oneplus": 1.8,
    }
    brand_factor = brand_multiplier.get(phone_features.brand.lower(), 1.5)
    
    # Calculate mock price based on specs
    predicted_price = (
        base_price * brand_factor +
        phone_features.ram * 50 +
        phone_features.storage * 0.5 +
        phone_features.battery_capacity * 0.05 +
        phone_features.screen_size * 30 +
        phone_features.camera_mp * 3
    )
    
    return round(predicted_price, 2)
