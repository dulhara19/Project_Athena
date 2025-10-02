# app/agents/athena_state.py
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# if you use redis, uncomment
# import redis
# r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

STATE_FILE = os.path.join(os.path.dirname(__file__), "athena_state.json")
MAX_EVENTS = 200

def clamp(x, a=-1.0, b=1.0):
    return max(a, min(b, float(x)))

def now_iso():
    return datetime.utcnow().isoformat()

# -------------------------
# Default template for Athena emotional state
# -------------------------
def default_state() -> Dict[str, Any]:
    return {
        "updated_at": now_iso(),
        # Valence, Arousal, Dominance in [-1..1] (V: -1 sad -> +1 happy)
        "vad": {"valence": 0.0, "arousal": 0.0, "dominance": 0.0},
        # discrete emotion distribution (label -> score)
        "emotions": {},
        # aggregate scalars (pain: -1 sadness -> +1 happiness)
        "pain": 0.0,
        "happiness": 0.0,
        # derived / meta
        "mood_label": "neutral",   # optional human-friendly label
        # history of events that changed state (bounded)
        "events": []  # each event: {"ts":..., "type": "...", "source":"user|internal", "delta": {...}, "note": "..."}
    }

# -------------------------
# Load / Save
# -------------------------
def load_state(file_path: Optional[str] = None) -> Dict[str, Any]:
    file_path = file_path or STATE_FILE
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # fallback to default on corruption
            return default_state()
    return default_state()

def save_state(state: Dict[str, Any], file_path: Optional[str] = None):
    file_path = file_path or STATE_FILE
    state["updated_at"] = now_iso()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# -------------------------
# Compute derived values
# -------------------------
def compute_pain_from_valence(valence: float, intensity: float = 1.0) -> float:
    """
    Map valence [-1..1] and intensity [0..1] -> pain in [-1..1]
    (negative valence -> negative pain; positive -> positive)
    """
    pain = clamp(valence * intensity)  # simple linear mapping - tune as needed
    return round(pain, 3)

def update_mood_label(state: Dict[str, Any]):
    v = state["vad"].get("valence", 0.0)
    if v <= -0.6:
        label = "very_sad"
    elif v <= -0.2:
        label = "sad"
    elif v < 0.2:
        label = "neutral"
    elif v < 0.6:
        label = "happy"
    else:
        label = "very_happy"
    state["mood_label"] = label

# -------------------------
# Merge emotion analysis output into Athena state
# Expected emotion_analysis shape (as in your pipeline):
# {"emotions": {...}, "vad": {"valence":..., "arousal":..., "dominance":...}, "intensity":..., "confidence": ...}
# -------------------------
def apply_emotion_analysis(state: Dict[str, Any], analysis: Dict[str, Any], source: str = "user", note: str = ""):
    vad = analysis.get("vad", {})
    # Weighted update: combine existing VAD with the new one (alpha blending)
    alpha = 0.6  # how strongly external events move Athena (tuneable)
    for axis in ("valence", "arousal", "dominance"):
        incoming = float(vad.get(axis, 0.0))
        state["vad"][axis] = clamp((1 - alpha) * state["vad"].get(axis, 0.0) + alpha * incoming)

    # update discrete emotions: keep top-K by weighted average
    incoming_emotions = analysis.get("emotions", {}) or {}
    merged = dict(state.get("emotions", {}))  # copy
    for k, v in incoming_emotions.items():
        prev = merged.get(k, 0.0)
        merged[k] = clamp((1 - alpha) * prev + alpha * float(v))
    # optional: keep only top 20
    top_items = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:30]
    state["emotions"] = {k: v for k, v in top_items}

    # intensity -> adjust pain/happiness
    intensity = float(analysis.get("intensity", max(incoming_emotions.values()) if incoming_emotions else 0.0))
    new_pain = compute_pain_from_valence(state["vad"]["valence"], intensity=intensity)
    state["pain"] = new_pain
    # happiness mirrored as positive pain
    state["happiness"] = round(max(0.0, state["vad"]["valence"]) * intensity, 3)

    # event log
    evt = {
        "ts": now_iso(),
        "type": "emotion_analysis",
        "source": source,
        "delta_vad": dict(state["vad"]),
        "note": note
    }
    push_event(state, evt)

    update_mood_label(state)
    return state

# -------------------------
# Apply a small event that nudges Athena's state
# event: {"type": "insult"|"praise"|"question"|"internal_action", "impact": float ([-1..1])}
# -------------------------
def apply_event(state: Dict[str, Any], event: Dict[str, Any]):
    typ = event.get("type", "generic")
    impact = float(event.get("impact", 0.0))  # -1..1 where negative causes sadness
    # map impact to V/A/D deltas (simple heuristic)
    if typ == "insult" or typ == "rejection":
        dv, da, dd = impact * -0.6, abs(impact) * 0.3, -abs(impact) * 0.2
    elif typ == "praise" or typ == "validation":
        dv, da, dd = impact * 0.6, abs(impact) * 0.2, abs(impact) * 0.1
    elif typ == "support_offer":
        dv, da, dd = 0.2 * impact, 0.1 * impact, 0.0
    else:
        # generic emotional nudge
        dv, da, dd = impact * 0.3, impact * 0.1, 0.0

    # apply (small step)
    state["vad"]["valence"] = clamp(state["vad"].get("valence", 0.0) + dv)
    state["vad"]["arousal"] = clamp(state["vad"].get("arousal", 0.0) + da)
    state["vad"]["dominance"] = clamp(state["vad"].get("dominance", 0.0) + dd)

    # recompute pain/happiness
    state["pain"] = compute_pain_from_valence(state["vad"]["valence"], intensity=abs(impact))
    state["happiness"] = round(max(0.0, state["vad"]["valence"]) * abs(impact), 3)

    evt = {
        "ts": now_iso(),
        "type": typ,
        "source": event.get("source", "system"),
        "impact": impact,
        "note": event.get("note", "")
    }
    push_event(state, evt)
    update_mood_label(state)
    return state

# -------------------------
# event history helper
# -------------------------
def push_event(state: Dict[str, Any], evt: Dict[str, Any]):
    lst: List[Dict[str, Any]] = state.setdefault("events", [])
    lst.append(evt)
    if len(lst) > MAX_EVENTS:
        # keep most recent
        state["events"] = lst[-MAX_EVENTS:]

# -------------------------
# decay function (call periodically)
# -------------------------
def decay_toward_neutral(state: Dict[str, Any], decay_rate: float = 0.02):
    """
    Gradually moves V/A/D toward 0.0 by 'decay_rate' fraction of current value.
    Call this between turns (e.g., every message or time tick).
    """
    for axis in ("valence", "arousal", "dominance"):
        cur = state["vad"].get(axis, 0.0)
        # move toward zero by fraction
        state["vad"][axis] = clamp(cur - decay_rate * cur)
    # recompute pain/happiness from new valence
    state["pain"] = compute_pain_from_valence(state["vad"]["valence"], intensity=0.5)
    state["happiness"] = round(max(0.0, state["vad"]["valence"]), 3)
    update_mood_label(state)
    return state

# -------------------------
# Example small wrapper to update Athena from a user turn
# -------------------------
def on_user_turn(state: Dict[str, Any], user_text: str, emotion_analysis: Dict[str, Any]):
    """
    Typical use: call analyze_emotion_text(user_text) -> emotion_analysis then:
        state = on_user_turn(state, user_text, emotion_analysis)
    """
    # 1) apply the emotion analysis
    apply_emotion_analysis(state, emotion_analysis, source="user", note=user_text)

    # 2) small event heuristics (if user insulted)
    txt = (user_text or "").lower()
    if any(k in txt for k in ["i hate you", "hate you", "you suck", "die"]):
        apply_event(state, {"type": "insult", "impact": -0.9, "source": "user", "note": user_text})
    elif any(k in txt for k in ["thank you", "love you", "i love you", "you are kind"]):
        apply_event(state, {"type": "praise", "impact": 0.6, "source": "user", "note": user_text})

    # 3) decay a bit after processing turn
    decay_toward_neutral(state, decay_rate=0.02)

    # 4) persist/update storage
    save_state(state)
    # optionally push to redis: r.hset(f"athena:state", mapping=state) but convert nested to json strings

    return state

# -------------------------
# Small example usage
# -------------------------
if __name__ == "__main__":
    s = load_state()
    print("before:", s["vad"], s["pain"])
    # dummy analysis (would be produced by your HF pipeline)
    fake_analysis = {
        "emotions": {"sadness": 0.6, "anger": 0.1},
        "vad": {"valence": -0.6, "arousal": 0.4, "dominance": 0.1},
        "intensity": 0.6,
        "confidence": 0.85
    }
    s = on_user_turn(s, "I hate you Athena", fake_analysis)
    print("after:", s["vad"], s["pain"], s["mood_label"])
