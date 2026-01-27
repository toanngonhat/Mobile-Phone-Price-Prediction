"""User routes for price prediction"""
from fastapi import APIRouter, HTTPException
from app.models.phone_features import PhoneFeatures, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()
prediction_service = PredictionService()


@router.post("/predict", response_model=PredictionResponse)
async def predict_price(features: PhoneFeatures):
    """Predict mobile phone price based on features"""
    try:
        price = prediction_service.predict(features)
        return PredictionResponse(
            predicted_price=price,
            features=features
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/features")
async def get_feature_info():
    """Get information about required features for prediction"""
    return {
        "features": {
            "battery_power": "Battery capacity in mAh",
            "blue": "Has Bluetooth (0 or 1)",
            "clock_speed": "Processor clock speed in GHz",
            "dual_sim": "Supports dual SIM (0 or 1)",
            "fc": "Front camera megapixels",
            "four_g": "Has 4G support (0 or 1)",
            "int_memory": "Internal memory in GB",
            "m_dep": "Mobile depth in cm",
            "mobile_wt": "Weight in grams",
            "n_cores": "Number of processor cores",
            "pc": "Primary camera megapixels",
            "px_height": "Pixel resolution height",
            "px_width": "Pixel resolution width",
            "ram": "RAM in MB",
            "sc_h": "Screen height in cm",
            "sc_w": "Screen width in cm",
            "talk_time": "Battery talk time in hours",
            "three_g": "Has 3G support (0 or 1)",
            "touch_screen": "Has touch screen (0 or 1)",
            "wifi": "Has WiFi (0 or 1)"
        }
    }
