"""Data utility helpers for dataset validation and summary."""
from __future__ import annotations

import pandas as pd

from app.config.settings import RAW_SCHEMA


def validate_schema(df: pd.DataFrame) -> None:
    missing = [col for col in RAW_SCHEMA if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset schema mismatch. Missing columns: {missing}")


def dataset_summary(df: pd.DataFrame) -> dict:
    validate_schema(df)
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "brand_count": int(df["device_brand"].nunique()),
        "year_range": {
            "min": int(df["release_year"].min()),
            "max": int(df["release_year"].max()),
        },
        "contains_4g": "4g" in df.columns,
        "contains_5g": "5g" in df.columns,
    }
