"""Admin routes for managing the application"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.roles import require_admin
from app.services.model_loader import ModelLoader

router = APIRouter()


@router.get("/stats")
async def get_stats(user=Depends(require_admin)):
    """Get application statistics (admin only)"""
    return {
        "total_predictions": 0,
        "model_version": "1.0.0",
        "status": "active"
    }


@router.post("/reload-model")
async def reload_model(user=Depends(require_admin)):
    """Reload the prediction model (admin only)"""
    try:
        model_loader = ModelLoader()
        model_loader.load_model()
        return {"message": "Model reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")


@router.get("/users")
async def list_users(user=Depends(require_admin)):
    """List all users (admin only)"""
    return {
        "users": [],
        "total": 0
    }
