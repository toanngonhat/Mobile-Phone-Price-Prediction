"""
Main application entry point for the Mobile Phone Price Prediction API.
Responsible for FastAPI app initialization and route registration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import admin, user, auth

app = FastAPI(
    title="Mobile Phone Price Prediction API",
    description="Backend API for predicting mobile phone prices based on specifications",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(user.router, prefix="/api/user", tags=["User"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Mobile Phone Price Prediction API",
        "status": "running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
