import os
import json

# Map user MBTI → suggested Athena MBTI to reduce mismatch
mbti_compatibility = {
    "INTJ": "ENFP",
    "INTP": "ESFJ",
    "ENTJ": "INFP",
    "ENTP": "INFJ",
    "INFJ": "ENTP",
    "INFP": "ENTJ",
    "ENFJ": "ISTP",
    "ENFP": "ISTJ",
    "ISTJ": "ESFP",
    "ISFJ": "ESTP",
    "ESTJ": "INFP",
    "ESFJ": "INTP",
    "ISTP": "ENFJ",
    "ISFP": "ENTJ",
    "ESTP": "ISFJ",
    "ESFP": "ISTJ"
}
def pick_new_personality_by_user_mbti(user_mbti, personalities_list):
    # Get suggested Athena MBTI from the mapping
    suggested_mbti = mbti_compatibility.get(user_mbti, None)
    if not suggested_mbti:
        return None  # fallback: no change

    # Find the personality in personalities_list
    for p in personalities_list:
        if p["mbti"] == suggested_mbti:
            return p
    return None  # fallback if not found

import json

# Load Athena profile from JSON


# Load Athena profile from JSON
def load_athena_profile(file_path=None):
    if file_path is None:
        # Get the directory of this Python file
        dir_path = os.path.dirname(__file__)
        # Join with the JSON file inside the same directory
        file_path = os.path.join(dir_path, "athena_profile.json")
    
    # Open and read the JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    return profile
# Get Athena MBTI
def get_athena_mbti(profile):
    """
    Returns Athena's current MBTI string and the full MBTI dict
    """
    mbti_info = profile.get("mbti", {})
    mbti_type = mbti_info.get("mbti", "")  # e.g., "ENFJ"
    return mbti_type, mbti_info

# Example usage
athena_profile = load_athena_profile()
athena_mbti_type, athena_mbti_info = get_athena_mbti(athena_profile)
print("Athena MBTI:", athena_mbti_type)
print("Full MBTI info:", athena_mbti_info)
