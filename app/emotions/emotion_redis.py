# emotion_redis.py
import redis
from transformers import pipeline
from typing import Dict, Any
import json
from datetime import datetime

# -----------------------------
# 1️⃣ Redis Setup
# -----------------------------
# Connect to local Redis for short-term memory
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# -----------------------------
# 2️⃣ Load GoEmotions Pipeline
# -----------------------------
print("Loading GoEmotions model...")
classifier = pipeline(
    "text-classification",
    model="joeddav/distilbert-base-uncased-go-emotions-student",
    top_k=None
)
print("Model loaded.")
print("Device set to use cpu")

# -----------------------------
# 3️⃣ VAD Map for emotions
# -----------------------------
VAD_MAP = {
    "admiration": (0.8, 0.4, 0.7),
    "amusement": (0.9, 0.6, 0.5),
    "anger": (-0.8, 0.8, 0.6),
    "annoyance": (-0.5, 0.7, 0.5),
    "approval": (0.7, 0.3, 0.6),
    "caring": (0.8, 0.4, 0.7),
    "confusion": (-0.3, 0.2, 0.0),
    "curiosity": (0.5, 0.6, 0.5),
    "desire": (0.6, 0.7, 0.6),
    "disappointment": (-0.7, 0.5, 0.4),
    "disapproval": (-0.8, 0.4, 0.5),
    "fear": (-0.9, 0.7, 0.4),
    "gratitude": (0.8, 0.3, 0.6),
    "joy": (1.0, 0.7, 0.7),
    "love": (0.9, 0.6, 0.8),
    "relief": (0.7, 0.2, 0.6),
    "sadness": (-1.0, 0.3, 0.2),
    "surprise": (0.5, 0.8, 0.5),
    "neutral": (0.0, 0.0, 0.0)
}
DEFAULT_VAD = (0.0, 0.0, 0.0)

# -----------------------------
# 4️⃣ Analyze user text emotions
# -----------------------------
def analyze_emotion_text(text: str) -> Dict[str, Any]:
    """
    Detect emotions from user text, calculate VAD and intensity.
    Handles outputs from HF pipeline safely.
    """
    out = classifier(text, top_k=None)

    # Handle flat list of dicts
    if isinstance(out, list) and all(isinstance(item, dict) for item in out):
        scores = {item["label"]: float(item["score"]) for item in out if "label" in item and "score" in item}
    else:
        raise ValueError(f"Unexpected classifier output: {out}")

    # Aggregate VAD
    valence = arousal = dominance = total_weight = 0.0
    for label, score in scores.items():
        vad = VAD_MAP.get(label.lower(), DEFAULT_VAD)
        valence += vad[0] * score
        arousal += vad[1] * score
        dominance += vad[2] * score
        total_weight += score

    if total_weight > 0:
        valence /= total_weight
        arousal /= total_weight
        dominance /= total_weight

    intensity = max(scores.values()) if scores else 0.0
    confidence = float(sum(scores.values()) / len(scores)) if scores else 0.0

    return {
        "emotions": scores,
        "vad": {"valence": float(valence), "arousal": float(arousal), "dominance": float(dominance)},
        "intensity": float(intensity),
        "confidence": float(confidence)
    }

# -----------------------------
# 5️⃣ Redis short-term memory
# -----------------------------
def store_user_emotion(user_id: str, emotion_data: dict):
    """
    Store user emotion in Redis with timestamp.
    """
    key = f"user:{user_id}:emotions"
    timestamp = datetime.now().isoformat()
    entry = {"timestamp": timestamp, "emotion": emotion_data}
    r.rpush(key, json.dumps(entry))
    r.expire(key, 3600*24)  # keep for 24 hours

def get_recent_emotions(user_id: str, n: int = 5):
    """
    Get last n emotions from Redis.
    """
    key = f"user:{user_id}:emotions"
    entries = r.lrange(key, -n, -1)
    return [json.loads(e) for e in entries]

# -----------------------------
# 6️⃣ Personality detection
# -----------------------------
def detect_personality(user_text: str) -> Dict[str, Any]:
    """
    Simple placeholder for personality detection (expand later)
    """
    traits = []
    text = user_text.lower()
    if any(x in text for x in ["i feel", "i am sad", "depressed"]):
        traits.append("emotional")
    if any(x in text for x in ["plan", "goal", "achieve"]):
        traits.append("analytical")
    if any(x in text for x in ["help others", "care", "support"]):
        traits.append("empathetic")
    return {"personality_traits": traits, "sample_text": user_text}

# -----------------------------
# 7️⃣ User pain detection
# -----------------------------
def detect_user_pain(emotions: dict) -> float:
    """
    Calculate a simple user pain level from VAD and intensity
    """
    vad = emotions.get("vad", {})
    valence = vad.get("valence", 0.0)
    intensity = emotions.get("intensity", 0.0)
    # Negative valence = higher pain
    pain_level = -valence * intensity
    return round(pain_level, 3)

# -----------------------------
# 8️⃣ High-level analyzer
# -----------------------------
def analyze_user(user_id: str, text: str):
    """
    Analyze user: emotions, personality, pain, and store in Redis
    """
    emotion_data = analyze_emotion_text(text)
    store_user_emotion(user_id, emotion_data)
    personality = detect_personality(text)
    pain = detect_user_pain(emotion_data)
    recent = get_recent_emotions(user_id)
    return {
        "user_id": user_id,
        "text": text,
        "emotions": emotion_data,
        "personality": personality,
        "pain_level": pain,
        "recent_memory": recent
    }

# -----------------------------
# 9️⃣ Test run
# -----------------------------
# if __name__ == "__main__":
#     user_id = "user123"
#     texts = "I want to die"
    
    
#     result = analyze_user(user_id, texts)

# # Only print current emotion state
# # print(json.dumps(result["emotions"], indent=4))

# # Or if you want both text + current emotions
# print(json.dumps({
#     "text": result["text"],
#     "emotions": result["emotions"]
# }, indent=4))


# =====================================

import matplotlib.pyplot as plt

# Function 1: Clear user memory
def clear_memory(user_result):
    """
    Clears the recent memory of the user.
    
    Parameters:
        user_result (dict): The result dictionary returned from analyze_user.
    
    Returns:
        dict: The updated result dictionary with recent_memory cleared.
    """
    user_result["recent_memory"] = []
    return user_result


# Function 2: Plot emotions and pain level
def plot_emotions_pain(emotions, pain_level, title="User Emotional State"):
    """
    Plots the emotions and pain level of the user.
    
    Parameters:
        emotions (dict): The 'emotions' dictionary from user result.
        pain_level (float): The 'pain_level' from user result.
        title (str): Optional title for the plot.
    """
    # Get top emotions (you can choose all or top N)
    emotion_scores = emotions["emotions"]
    
    # Sort emotions by score descending
    sorted_emotions = dict(sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # Plot
    plt.figure(figsize=(10, 6))
    
    # Emotion bar plot
    plt.bar(sorted_emotions.keys(), sorted_emotions.values(), color='skyblue')
    plt.ylabel("Emotion Score")
    plt.title(title)
    
    # Overlay pain level
    plt.axhline(y=pain_level, color='red', linestyle='--', label=f"Pain Level: {pain_level}")
    plt.legend()
    plt.xticks(rotation=45)
    
    plt.show()


# Example usage:
if __name__ == "__main__":
    user_result = analyze_user("user123", "I want to die")
    
    # Clear memory if needed
    # user_result = clear_memory(user_result)
    
    # Plot current emotional state and pain level
    plot_emotions_pain(user_result["emotions"], user_result["pain_level"])
