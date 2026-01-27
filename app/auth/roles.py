"""Role-based access control for the application"""
import os
from fastapi import HTTPException, Header
from typing import Optional


class UserRole:
    """User role definitions"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


def get_current_user(x_api_key: Optional[str] = Header(None)):
    """
    Get current user from API key
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        User information dictionary
    """
    # This is a simplified implementation
    # In production, you would validate against a database
    
    if x_api_key is None:
        return {"role": UserRole.GUEST, "username": "guest"}
    
    # Validate API key against environment variable
    admin_key = os.environ.get("ADMIN_API_KEY", "admin-key-123")  # Fallback for development only
    
    if x_api_key == admin_key:
        return {"role": UserRole.ADMIN, "username": "admin"}
    elif x_api_key.startswith("user-"):
        return {"role": UserRole.USER, "username": "user"}
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")


def require_admin(x_api_key: Optional[str] = Header(None)):
    """
    Dependency to require admin role
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        User information if admin, raises HTTPException otherwise
    """
    user = get_current_user(x_api_key)
    
    if user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return user


def require_user(x_api_key: Optional[str] = Header(None)):
    """
    Dependency to require user role (or higher)
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        User information if user or admin, raises HTTPException otherwise
    """
    user = get_current_user(x_api_key)
    
    if user["role"] == UserRole.GUEST:
        raise HTTPException(
            status_code=403,
            detail="User access required"
        )
    
    return user
