"""
LLM connector module for communicating with Ollama.
"""
import requests
import json
from typing import Optional
from app.config import config
from app.utils.logger import logger
from app.utils.error_handler import LLMConnectionError, handle_error


def connector(prompt: str, timeout: int = 30) -> requests.Response:
    """
    Connect to LLM API and send prompt.
    
    Args:
        prompt: The prompt text to send
        timeout: Request timeout in seconds
        
    Returns:
        Response object from LLM API
        
    Raises:
        LLMConnectionError: If connection fails
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    url = config.LLM_URL
    headers = {'Content-Type': 'application/json'}
    data = {
        'model': config.LLM_MODEL,
        'prompt': prompt,
        'stream': False,
    }
    
    try:
        logger.debug(f"Sending prompt to LLM ({config.LLM_MODEL})")
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data),
            timeout=timeout
        )
        response.raise_for_status()
        logger.debug("LLM response received successfully")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM connection failed: {e}")
        handle_error(e, {"function": "connector", "url": url})
        raise LLMConnectionError(f"Failed to connect to LLM: {e}")
