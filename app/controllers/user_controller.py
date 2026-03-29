"""User controller for prediction workflows."""
from __future__ import annotations

from app.models.phone_price_model import PhonePriceModel


def predict_price(features: dict) -> float:
    model = PhonePriceModel()
    return model.predict(features)
