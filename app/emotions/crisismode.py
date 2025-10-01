import json
from typing import List, Dict

NEGATIVE_WORDS = ["die", "suicide", "hate", "sad", "depressed", "alone", "worthless", "unhappy"]

USER_PAIN_LOG_FILE = "user_pain_log.json"  # file storing recent messages with emotion & pain

def load_user_pain_log(user_id: str) -> List[Dict]:
    """Load the user's recent messages from JSON file."""
    try:
        with open(USER_PAIN_LOG_FILE, "r") as f:
            data = json.load(f)
        # filter for this user
        return data.get(user_id, [])
    except Exception:
        return []

def is_negative(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in NEGATIVE_WORDS)

def check_crisis_mode(user_id: str, current_input: str) -> Dict:
    """
    Checks if crisis mode should be triggered based on last 3 user inputs and current input.
    Returns emotional state, pain, personality, recent inputs if triggered.
    """
    # Step 1: Only proceed if current input is negative
    if not is_negative(current_input):
        return {"crisis_mode": False}

    # Step 2: Load recent messages from JSON
    recent_msgs = load_user_pain_log(user_id)
    # get the last 2 messages + current input to make 3 total
    last_three = recent_msgs[-2:] + [{"text": current_input, "emotion": {}, "pain": 0.0}]
    if len(last_three) < 3:
        return {"crisis_mode": False}  # not enough data

    # Step 3: Check if all three are negative
    negative_flags = [is_negative(m["text"]) or m.get("pain", 0.0) < 0 for m in last_three]
    if all(negative_flags):
        # Crisis triggered → return required info
        emotional_state = last_three[-1].get("emotion", {})
        pain_levels = [m.get("pain", 0.0) for m in last_three]
        recent_inputs = [m["text"] for m in last_three]
        personality = last_three[-1].get("personality", {})  # assuming personality stored per input
        return {
            "crisis_mode": True,
            "emotional_state": emotional_state,
            "pain_levels": pain_levels,
            "personality": personality,
            "recent_inputs": recent_inputs
        }

    return {"crisis_mode": False}
