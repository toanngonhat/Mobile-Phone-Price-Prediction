"""
Data utilities for dataset handling and preprocessing.
Provides functions for loading, saving, and analyzing datasets.
"""
import os
import pandas as pd
from fastapi import UploadFile


async def save_dataset(file: UploadFile) -> str:
    """
    Save uploaded CSV dataset to data directory.
    Returns the file path.
    """
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return file_path


def get_dataset_statistics(file_path: str) -> dict:
    """
    Generate statistics for the uploaded dataset.
    Returns summary information about the data.
    
    TODO: Add more detailed statistical analysis
    TODO: Add data quality checks
    """
    df = pd.read_csv(file_path)
    
    stats = {
        "total_records": len(df),
        "columns": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "shape": df.shape,
    }
    
    # Add price range if price column exists
    price_columns = [col for col in df.columns if 'price' in col.lower()]
    if price_columns:
        price_col = price_columns[0]
        stats["price_range"] = {
            "min": float(df[price_col].min()),
            "max": float(df[price_col].max()),
            "mean": float(df[price_col].mean()),
            "median": float(df[price_col].median())
        }
    
    return stats
