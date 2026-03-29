"""Central settings for predictor system."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "app" / "data" / "sample_phone_data.csv"

PACKAGE_DIR = BASE_DIR / "app"
MODEL_VERSIONS_DIR = PACKAGE_DIR / "model_versions"
APP_SETTINGS_PATH = PACKAGE_DIR / "app_settings.json"

KAGGLE_DATASET_REF = "ahsan81/used-handheld-device-data"
KAGGLE_FILE_NAME = "used_device_data.csv"

FEATURE_COLUMNS = ["brand", "ram", "storage", "battery_capacity", "screen_size", "camera_mp"]
RAW_SCHEMA = [
    "device_brand",
    "os",
    "screen_size",
    "rear_camera_mp",
    "front_camera_mp",
    "internal_memory",
    "ram",
    "battery",
    "weight",
    "release_year",
    "days_used",
    "normalized_used_price",
    "normalized_new_price",
]
