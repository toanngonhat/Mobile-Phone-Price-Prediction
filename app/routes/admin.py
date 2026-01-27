"""
Admin routes for managing datasets and ML models.
Handles file uploads, model replacement, and dataset statistics.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.auth.roles import verify_admin_role
from app.utils.data_utils import save_dataset, get_dataset_statistics
from app.services.model_loader import save_model
import os

router = APIRouter()


@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    _: str = Depends(verify_admin_role)
):
    """
    Upload training dataset (CSV format).
    Only accessible by Admin users.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    try:
        # Save dataset to data directory
        file_path = await save_dataset(file)

        # Get basic statistics
        stats = get_dataset_statistics(file_path)

        return {
            "message": "Dataset uploaded successfully",
            "filename": file.filename,
            "path": file_path,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading dataset: {str(e)}")


@router.post("/upload-model")
async def upload_model(
    file: UploadFile = File(...),
    _: str = Depends(verify_admin_role)
):
    """
    Upload or replace trained ML model file.
    Only accessible by Admin users.
    TODO: Add model validation and versioning
    """
    try:
        # Save model file
        model_path = await save_model(file)

        return {
            "message": "Model uploaded successfully",
            "filename": file.filename,
            "path": model_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading model: {str(e)}")


@router.get("/dataset-stats")
async def get_dataset_stats(_: str = Depends(verify_admin_role)):
    """
    View statistics of the current training dataset.
    Only accessible by Admin users.
    """
    dataset_path = "data/sample_phone_data.csv"

    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="No dataset found")

    try:
        stats = get_dataset_statistics(dataset_path)
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
