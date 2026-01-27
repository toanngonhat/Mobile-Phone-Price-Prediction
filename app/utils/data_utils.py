"""Data utility functions for preprocessing and feature engineering"""
import numpy as np
from app.models.phone_features import PhoneFeatures


def prepare_features(features: PhoneFeatures) -> np.ndarray:
    """
    Convert PhoneFeatures object to numpy array for model input
    
    Args:
        features: PhoneFeatures object containing phone specifications
        
    Returns:
        Numpy array of features in the correct order
    """
    feature_array = np.array([
        features.battery_power,
        features.blue,
        features.clock_speed,
        features.dual_sim,
        features.fc,
        features.four_g,
        features.int_memory,
        features.m_dep,
        features.mobile_wt,
        features.n_cores,
        features.pc,
        features.px_height,
        features.px_width,
        features.ram,
        features.sc_h,
        features.sc_w,
        features.talk_time,
        features.three_g,
        features.touch_screen,
        features.wifi
    ])
    
    return feature_array


def normalize_features(features: np.ndarray) -> np.ndarray:
    """
    Normalize feature values
    
    Args:
        features: Raw feature array
        
    Returns:
        Normalized feature array
    """
    # Simple min-max normalization
    # In production, use saved scaler from training
    return features


def validate_phone_data(data: dict) -> bool:
    """
    Validate phone data dictionary
    
    Args:
        data: Dictionary containing phone features
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        'battery_power', 'blue', 'clock_speed', 'dual_sim', 'fc',
        'four_g', 'int_memory', 'm_dep', 'mobile_wt', 'n_cores',
        'pc', 'px_height', 'px_width', 'ram', 'sc_h', 'sc_w',
        'talk_time', 'three_g', 'touch_screen', 'wifi'
    ]
    
    return all(field in data for field in required_fields)


def calculate_screen_area(sc_h: float, sc_w: float) -> float:
    """
    Calculate screen area from height and width
    
    Args:
        sc_h: Screen height in cm
        sc_w: Screen width in cm
        
    Returns:
        Screen area in square cm
    """
    return sc_h * sc_w


def calculate_pixel_density(px_height: int, px_width: int, screen_area: float) -> float:
    """
    Calculate pixel density
    
    Args:
        px_height: Pixel resolution height
        px_width: Pixel resolution width
        screen_area: Screen area in square cm
        
    Returns:
        Pixel density
    """
    if screen_area == 0:
        return 0
    
    total_pixels = px_height * px_width
    return total_pixels / screen_area
