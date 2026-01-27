"""
User routes for phone price prediction.
Handles specification input and returns predicted prices.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.roles import verify_user_role
from app.models.phone_features import PhoneFeatures, PricePredictionResponse
from app.services.prediction_service import predict_price

router = APIRouter()


@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_phone_price(
    phone: PhoneFeatures,
    _: str = Depends(verify_user_role)
):
    """
    Predict mobile phone price based on specifications.
    Accessible by User and Admin roles.
    """
    try:
        predicted_price = predict_price(phone)

        return PricePredictionResponse(
            predicted_price=predicted_price,
            features=phone,
            model_version="mock-v1.0"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get("/health")
async def user_health_check():
    """User API health check - no authentication required"""
    return {"status": "ok", "service": "user"}
