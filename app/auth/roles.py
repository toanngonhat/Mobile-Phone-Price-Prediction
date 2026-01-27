"""
Role-based access control utilities.
Manages user roles (Admin, User) and authorization checks.
"""
from enum import Enum
from fastapi import Header, HTTPException, status
from typing import Optional


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"


def parse_token(token: str) -> tuple[str, str]:
    """
    Parse the simple token format: username:role
    In production, use proper JWT token validation.

    Args:
        token: Token string in format "username:role"

    Returns:
        Tuple of (username, role)
    """
    try:
        username, role = token.split(":")
        return username, role
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )


def verify_admin_role(authorization: Optional[str] = Header(None, description="Bearer token")):
    """
    Dependency to verify admin role from token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required. Please login first."
        )

    # Extract token from "Bearer <token>" format
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    else:
        token = authorization

    username, role = parse_token(token)

    if role.lower() != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return {"username": username, "role": role}


def verify_user_role(authorization: Optional[str] = Header(None, description="Bearer token")):
    """
    Dependency to verify user or admin role from token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required. Please login first."
        )

    # Extract token from "Bearer <token>" format
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    else:
        token = authorization

    username, role = parse_token(token)

    if role.lower() not in [UserRole.ADMIN, UserRole.USER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Valid user role required"
        )

    return {"username": username, "role": role}
