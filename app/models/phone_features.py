"""
Pydantic models for phone features and API request/response schemas.
Defines the structure of mobile phone specifications.
"""
from pydantic import BaseModel, Field
from typing import Optional


class PhoneFeatures(BaseModel):
    """Phone specification input model for price prediction"""
    brand: str = Field(..., description="Phone brand/manufacturer")
    ram: int = Field(..., ge=1, le=32, description="RAM in GB")
    storage: int = Field(..., ge=8, le=1024, description="Storage in GB")
    battery_capacity: int = Field(..., ge=1000, le=10000, description="Battery capacity in mAh")
    screen_size: float = Field(..., ge=3.0, le=10.0, description="Screen size in inches")
    camera_mp: int = Field(..., ge=2, le=200, description="Main camera megapixels")


class PricePredictionResponse(BaseModel):
    """Response model for price prediction"""
    predicted_price: float = Field(..., description="Predicted price in USD")
    features: PhoneFeatures
    model_version: str = Field(default="mock-v1.0", description="ML model version used")


class DatasetStats(BaseModel):
    """Statistics about the uploaded dataset"""
    total_records: int
    columns: list[str]
    missing_values: dict
    price_range: Optional[dict] = None
