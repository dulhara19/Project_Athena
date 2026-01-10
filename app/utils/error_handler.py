"""
Centralized error handling utilities.
"""
from typing import Any, Dict, Optional
from app.utils.logger import logger


class AthenaError(Exception):
    """Base exception for Athena system"""
    pass


class EmotionAnalysisError(AthenaError):
    """Error in emotion analysis"""
    pass


class LLMConnectionError(AthenaError):
    """Error connecting to LLM"""
    pass


class RedisConnectionError(AthenaError):
    """Error connecting to Redis"""
    pass


class EgoCalculationError(AthenaError):
    """Error in ego calculation"""
    pass


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle errors gracefully and return structured error response.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Dictionary with error information
    """
    error_info = {
        "error": True,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"Error occurred: {error_info}", exc_info=True)
    
    return error_info


def safe_float(value: Any, default: float = 0.0, min_val: float = -1.0, max_val: float = 1.0) -> float:
    """
    Safely convert value to float with clamping.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped float value
    """
    try:
        if isinstance(value, str):
            value = value.strip()
            if value.endswith("%"):
                value = float(value.rstrip("%")) / 100.0
            else:
                value = float(value)
        else:
            value = float(value)
        
        return max(min_val, min(max_val, value))
    except (ValueError, TypeError, AttributeError):
        logger.warning(f"Could not convert {value} to float, using default {default}")
        return default


def validate_pain_level(pain: Any) -> float:
    """
    Validate and normalize pain level to [-1, 1] range.
    
    Args:
        pain: Pain value (can be string, int, or float)
        
    Returns:
        Validated float pain level
    """
    return safe_float(pain, default=0.0, min_val=-1.0, max_val=1.0)

