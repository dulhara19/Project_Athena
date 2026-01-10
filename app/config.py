"""
Centralized configuration management for Athena system.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # LLM Configuration
    LLM_URL: str = os.getenv("LLM_URL", "http://localhost:11434/api/generate")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3:8b")
    
    # File Paths
    PAIN_LOG_FILE: str = os.getenv("PAIN_LOG_FILE", "pain_log.json")
    USER_PAIN_LOG_FILE: str = os.getenv("USER_PAIN_LOG_FILE", "user_pain_log.json")
    ATHENA_PROFILE_PATH: str = os.getenv(
        "ATHENA_PROFILE_PATH", 
        os.path.join(os.path.dirname(__file__), "agents", "athena_profile.json")
    )
    
    # Emotion Model
    EMOTION_MODEL: str = os.getenv(
        "EMOTION_MODEL", 
        "joeddav/distilbert-base-uncased-go-emotions-student"
    )
    
    # Crisis Mode
    CRISIS_CONSECUTIVE_COUNT: int = int(os.getenv("CRISIS_CONSECUTIVE_COUNT", "3"))
    
    # Ego System
    EGO_STRENGTH_DEFAULT: float = float(os.getenv("EGO_STRENGTH_DEFAULT", "0.75"))
    EGO_LEARNING_RATE: float = float(os.getenv("EGO_LEARNING_RATE", "0.05"))
    
    # Personality Adaptation
    BIG_MISMATCH_THRESHOLD: float = float(os.getenv("BIG_MISMATCH_THRESHOLD", "0.5"))
    
    # Memory
    REDIS_MAX_ENTRIES: int = int(os.getenv("REDIS_MAX_ENTRIES", "200"))
    REDIS_EXPIRATION_DAYS: int = int(os.getenv("REDIS_EXPIRATION_DAYS", "30"))
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)


# Global config instance
config = Config()

