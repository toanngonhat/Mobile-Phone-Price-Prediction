"""Main application entry point for Mobile Phone Price Prediction"""
from fastapi import FastAPI
from app.routes import admin, user

app = FastAPI(
    title="Mobile Phone Price Prediction API",
    description="API for predicting mobile phone prices based on features",
    version="1.0.0"
)

# Include routers
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(user.router, prefix="/api", tags=["user"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Mobile Phone Price Prediction API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
