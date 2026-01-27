"""
Simple authentication routes for login.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.auth.credentials import verify_credentials, get_user_role

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    message: str
    username: str
    role: str
    token: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - validates username and password.
    Returns user role and a simple token.
    """
    # Verify credentials
    if not verify_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Get user role
    role = get_user_role(credentials.username)

    # Generate simple token (username:role for demonstration)
    # In production, use JWT tokens
    token = f"{credentials.username}:{role}"

    return LoginResponse(
        message="Login successful",
        username=credentials.username,
        role=role,
        token=token
    )


@router.get("/check")
async def check_auth():
    """Check if authentication service is working"""
    return {
        "status": "ok",
        "service": "authentication",
        "message": "Authentication service is running"
    }
