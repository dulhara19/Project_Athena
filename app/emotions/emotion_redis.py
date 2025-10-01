# emotion_redis.py
import redis
from transformers import pipeline
from typing import Dict, Any
import json
from datetime import datetime

from app.emotions.mbti import detect_mbti_for_user
from app.emotions.emotionplotter import log_pain_status
from app.emotions.emotionplotter import plot_pain_history_fixed

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
def store_user_emotion(user_id: str, session_id: str, text: str, emotion_data: dict, pain: float, max_len: int = 200):
    """
    Store the user message and its emotion analysis in Redis.
    - user_id: user identifier
    - session_id: session identifier (optional but useful)
    - text: raw user message (string)
    - emotion_data: dict returned from analyze_emotion_text
    - pain: numeric pain level
    - max_len: max number of entries to keep in list
    """
    key = f"user:{user_id}:emotions"
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "ts": timestamp,
        "session_id": session_id,
        "text": text,
        "emotion": emotion_data,
        "pain": float(pain)
    }
    # push to right so chronological order is preserved (oldest on left)
    r.rpush(key, json.dumps(entry))
    # keep list bounded
    r.ltrim(key, -max_len, -1)
    # set expiration (e.g., 30 days) — tune as needed
    r.expire(key, 30 * 24 * 3600)



def get_recent_emotions(user_id: str, n: int = 5):
    """
    Return last n entries (most recent first) as parsed objects.
    """
    key = f"user:{user_id}:emotions"
    # LRANGE with negative indices: -n to -1 returns last n in chronological order,
    # but we want most-recent-first, so get -n..-1 then reverse
    raw_list = r.lrange(key, -n, -1)
    # If list is empty, raw_list == []
    parsed = [json.loads(x) for x in raw_list] if raw_list else []
    # reverse so most recent is first
    parsed.reverse()
    return parsed



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
    Calculate user pain level in range [-1, 1].
    -1 = maximum sadness
     0 = neutral
     1 = maximum happiness
    """
    vad = emotions.get("vad", {})
    valence = vad.get("valence", 0.0)   # -1 (sad) → +1 (happy)
    intensity = emotions.get("intensity", 1.0)  # 0 → 1 scaling

    # Simple scaling factor to amplify pain to visible range
    pain_level = valence * intensity * 10

    # Clamp to [-1, 1] and round to 2 decimals
    pain_level = max(-1.0, min(1.0, pain_level))
    return round(pain_level, 2)


 

# -----------------------------
# 8️⃣ High-level analyzer
# -----------------------------
def analyze_user(user_id: str, session_id: str, text: str):
    """
    Analyze user: emotions, personality, pain, and store in Redis (with text).
    """
    # Run emotion analysis
    emotion_data = analyze_emotion_text(text)

    # compute pain (you have detect_user_pain earlier; adapt if needed)
    pain = detect_user_pain(emotion_data)

    # store the text + analysis + pain + session info
    store_user_emotion(user_id=user_id, session_id=session_id, text=text, emotion_data=emotion_data, pain=pain)

    # personality detection (you can base on text or recent messages)
    personality = detect_personality(text)
    mbti=detect_mbti_for_user(user_id, days=10) 

    # Optional: logging / plotting
    try:
        log_pain_status(text, pain)
        plot_pain_history_fixed()
    except Exception:
        # plotting failures should not break analysis
        pass

    recent = get_recent_emotions(user_id, n=5)
    return {
        "user_id": user_id,
        "session_id": session_id,
        "text": text,
        "emotions": emotion_data,
        "personality": personality,
        "pain_level": pain,
        "recent_memory": recent,
        "mbti": mbti
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


# Example usage:
if __name__ == "__main__":
    user_result = analyze_user("user123", "session1","i love you")
    
#     # Clear memory if needed
#     # user_result = clear_memory(user_result)

# # Assuming `result` is the output from analyze_user
# recent_memory = user_result.get("recent_memory", [])

# # If you have pain_level inside each memory, make sure it exists; otherwise can add current pain
# for mem in recent_memory:
#     mem['pain_level'] = user_result.get('pain_level', 0)

# plot_emotions_pain(recent_memory, top_emotions=['sadness', 'anger', 'desire', 'joy'])
