"""
MedAI Assistant - FastAPI Application Entry Point

Initializes the FastAPI application with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.logging import LoggingMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MedAI Assistant",
    description="Medical AI Diagnostic System with Multi-Agent Architecture",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

logger.info("MedAI Assistant API Server Initialized")
logger.info(f"Allowed Origins: {allowed_origins}")


# ==================== ROUTES ====================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "ok",
        "service": "MedAI Assistant",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MedAI Assistant"
    }


# Import and include routers
try:
    from app.api.endpoints import conversations
    app.include_router(conversations.router, prefix="/api", tags=["conversations"])
    logger.info("✓ Conversations router loaded")
except Exception as e:
    logger.error(f"Failed to load conversations router: {str(e)}")

# Future routers will be added here
# - app.api.endpoints.auth
# - app.api.endpoints.patients
# - app.api.endpoints.studies
# - app.api.endpoints.images
# - app.api.endpoints.reports


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting up MedAI Assistant...")
    
    # Create necessary directories
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("✓ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down MedAI Assistant...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
