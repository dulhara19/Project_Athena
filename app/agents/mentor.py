"""
Athena mentor module - Profile management utilities.
Workflow orchestration has been moved to app/api/workflow.py
"""
import os
import json
from typing import Dict, Any, Tuple
from app.config import config
from app.utils.logger import logger
from app.utils.error_handler import handle_error


# -------------------------------
# File paths and profile utils
# -------------------------------
current_dir = os.path.dirname(__file__)
profile_path = os.path.join(current_dir, "athena_profile.json")


def load_athena_profile(file_path: str = None) -> Dict[str, Any]:
    """
    Load Athena's profile from JSON file.
    
    Args:
        file_path: Optional path to profile file
        
    Returns:
        Athena profile dictionary
    """
    if file_path is None:
        file_path = config.ATHENA_PROFILE_PATH if hasattr(config, 'ATHENA_PROFILE_PATH') else profile_path
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        logger.debug(f"Loaded Athena profile from {file_path}")
        return profile
    except FileNotFoundError:
        logger.error(f"Athena profile file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in profile file: {e}")
        raise


def get_athena_mbti(profile: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Extract MBTI information from Athena profile.
    
    Args:
        profile: Athena profile dictionary
        
    Returns:
        Tuple of (MBTI type string, full MBTI info dict)
    """
    mbti_info = profile.get("mbti", {})
    mbti_type = mbti_info.get("mbti", "") if isinstance(mbti_info, dict) else ""
    return mbti_type, mbti_info


def update_athena_mbti(file_path: str, new_mbti_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update Athena's MBTI personality in profile.
    
    Args:
        file_path: Path to profile file
        new_mbti_dict: New MBTI dictionary to set
        
    Returns:
        Updated MBTI dictionary
    """
    try:
        profile = load_athena_profile(file_path)
        profile["mbti"] = new_mbti_dict
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        logger.info("Updated Athena MBTI personality")
        return profile["mbti"]
    except Exception as e:
        logger.error(f"Failed to update Athena MBTI: {e}")
        handle_error(e, {"function": "update_athena_mbti", "file_path": file_path})
        raise