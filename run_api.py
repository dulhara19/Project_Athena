#!/usr/bin/env python3
"""
Script to run the Athena API server.
"""
import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

