"""
FastAPI application main file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.utils.logger import logger
from app.api.routes import chat, metrics, ego

# Initialize FastAPI app
app = FastAPI(
    title="Athena API",
    description="AI Agent with Enhanced Ego System and Empathy Metrics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL] if hasattr(config, 'FRONTEND_URL') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(ego.router, prefix="/api/v1", tags=["ego"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Athena API starting up...")
    logger.info(f"API running on {config.API_HOST}:{config.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Athena API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Athena API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

