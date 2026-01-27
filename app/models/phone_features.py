"""Data models for phone features and predictions"""
from pydantic import BaseModel, Field


class PhoneFeatures(BaseModel):
    """Phone features for price prediction"""
    
    battery_power: int = Field(..., description="Battery capacity in mAh", ge=500, le=2000)
    blue: int = Field(..., description="Has Bluetooth (0 or 1)", ge=0, le=1)
    clock_speed: float = Field(..., description="Processor clock speed in GHz", ge=0.5, le=3.0)
    dual_sim: int = Field(..., description="Supports dual SIM (0 or 1)", ge=0, le=1)
    fc: int = Field(..., description="Front camera megapixels", ge=0, le=20)
    four_g: int = Field(..., description="Has 4G support (0 or 1)", ge=0, le=1)
    int_memory: int = Field(..., description="Internal memory in GB", ge=2, le=256)
    m_dep: float = Field(..., description="Mobile depth in cm", ge=0.1, le=1.0)
    mobile_wt: int = Field(..., description="Weight in grams", ge=80, le=200)
    n_cores: int = Field(..., description="Number of processor cores", ge=1, le=8)
    pc: int = Field(..., description="Primary camera megapixels", ge=0, le=20)
    px_height: int = Field(..., description="Pixel resolution height", ge=0, le=1960)
    px_width: int = Field(..., description="Pixel resolution width", ge=500, le=1998)
    ram: int = Field(..., description="RAM in MB", ge=256, le=4000)
    sc_h: float = Field(..., description="Screen height in cm", ge=5, le=19)
    sc_w: float = Field(..., description="Screen width in cm", ge=0, le=18)
    talk_time: int = Field(..., description="Battery talk time in hours", ge=2, le=20)
    three_g: int = Field(..., description="Has 3G support (0 or 1)", ge=0, le=1)
    touch_screen: int = Field(..., description="Has touch screen (0 or 1)", ge=0, le=1)
    wifi: int = Field(..., description="Has WiFi (0 or 1)", ge=0, le=1)
    
    class Config:
        schema_extra = {
            "example": {
                "battery_power": 1500,
                "blue": 1,
                "clock_speed": 2.5,
                "dual_sim": 1,
                "fc": 5,
                "four_g": 1,
                "int_memory": 64,
                "m_dep": 0.5,
                "mobile_wt": 150,
                "n_cores": 4,
                "pc": 12,
                "px_height": 1920,
                "px_width": 1080,
                "ram": 3000,
                "sc_h": 15,
                "sc_w": 8,
                "talk_time": 10,
                "three_g": 1,
                "touch_screen": 1,
                "wifi": 1
            }
        }


class PredictionResponse(BaseModel):
    """Response model for price prediction"""
    
    predicted_price: float = Field(..., description="Predicted price in USD")
    features: PhoneFeatures = Field(..., description="Input features used for prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "predicted_price": 450.75,
                "features": {
                    "battery_power": 1500,
                    "blue": 1,
                    "clock_speed": 2.5,
                    "dual_sim": 1,
                    "fc": 5,
                    "four_g": 1,
                    "int_memory": 64,
                    "m_dep": 0.5,
                    "mobile_wt": 150,
                    "n_cores": 4,
                    "pc": 12,
                    "px_height": 1920,
                    "px_width": 1080,
                    "ram": 3000,
                    "sc_h": 15,
                    "sc_w": 8,
                    "talk_time": 10,
                    "three_g": 1,
                    "touch_screen": 1,
                    "wifi": 1
                }
            }
        }
