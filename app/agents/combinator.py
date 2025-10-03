from app.llmconnector import connector
import re
from typing import Dict, Any

def safe_str(x):
    return "" if x is None else str(x)

def parse_personality_desc(personality_desc: str) -> Dict[str, Any]:
    out = {"mbti": None, "confidence": None, "axis_scores": {}}
    if not personality_desc:
        return out
    m = re.search(r"MBTI:\s*([A-Z]{4})", personality_desc)
    if m:
        out["mbti"] = m.group(1)
    m = re.search(r"Confidence:\s*([0-9]*\.?[0-9]+)", personality_desc)
    if m:
        try:
            out["confidence"] = float(m.group(1))
        except:
            out["confidence"] = None
    m = re.search(r"Axis Scores:\s*(\{.*\})", personality_desc)
    if m:
        try:
            axis = eval(m.group(1), {"__builtins__": None}, {})
            if isinstance(axis, dict):
                out["axis_scores"] = axis
        except Exception:
            out["axis_scores"] = {}
    return out

def parse_emotion_desc(emotion_desc: str) -> Dict[str, float]:
    out = {"ego": None, "neutral": None}
    if not emotion_desc:
        return out
    m = re.search(r"Ego:\s*([-+]?[0-9]*\.?[0-9]+)", emotion_desc)
    if m:
        out["ego"] = float(m.group(1))
    m = re.search(r"neutral:\s*([-+]?[0-9]*\.?[0-9]+)", emotion_desc)
    if m:
        out["neutral"] = float(m.group(1))
    return out

def normalize_user_summary(user_summary: Dict[str, Any]) -> Dict[str, Any]:
    norm = {
        "latest_text": "",
        "personality": {"mbti": None, "confidence": None, "axis_scores": {}},
        "emotions": {"ego": None, "neutral": None},
        "memory_desc": None,
        "human_desc": None,
        "chat_history": [],
        "pain_level": 0.0,
        "user_id": None
    }

    # latest text
    if user_summary.get("latest_text"):
        norm["latest_text"] = safe_str(user_summary.get("latest_text"))
    elif user_summary.get("user_input"):
        norm["latest_text"] = safe_str(user_summary.get("user_input"))
    elif isinstance(user_summary.get("chat_history"), list) and user_summary["chat_history"]:
        last = user_summary["chat_history"][-1]
        if isinstance(last, dict):
            norm["latest_text"] = safe_str(last.get("query", "")) or safe_str(last)
        else:
            norm["latest_text"] = safe_str(last)

    # personality
    if isinstance(user_summary.get("personality"), dict):
        p = user_summary.get("personality", {})
        norm["personality"]["mbti"] = p.get("mbti") or p.get("MBTI")
        norm["personality"]["confidence"] = p.get("confidence")
        norm["personality"]["axis_scores"] = p.get("axis_scores", {})
    elif user_summary.get("personality_desc"):
        parsed = parse_personality_desc(user_summary.get("personality_desc"))
        norm["personality"].update(parsed)

    # emotions
    if isinstance(user_summary.get("emotions"), dict):
        norm["emotions"].update(user_summary.get("emotions"))
    elif user_summary.get("emotion_desc"):
        parsed_e = parse_emotion_desc(user_summary.get("emotion_desc"))
        norm["emotions"].update(parsed_e)

    # memory/human/chat
    norm["memory_desc"] = user_summary.get("memory_desc")
    norm["human_desc"] = user_summary.get("human_desc")
    norm["chat_history"] = user_summary.get("chat_history", [])
    if norm["human_desc"]:
        m = re.search(r"User ID:\s*([^\s,]+)", safe_str(norm["human_desc"]))
        if m:
            norm["user_id"] = m.group(1)
        else:
            norm["user_id"] = safe_str(norm["human_desc"])

    # pain_level fallback using ego
    ego = norm["emotions"].get("ego")
    try:
        if ego is not None:
            norm["pain_level"] = max(-1.0, min(1.0, float(ego)))
    except:
        norm["pain_level"] = 0.0

    return norm

def generate_final_response(user_summary: Dict[str, Any],
                            athena_profile: Dict[str, Any]) -> str:
    """
    Generates a textual empathetic response for Athena.
    Returns: final response string wrapped in <final_answer> tags.
    """
    norm = normalize_user_summary(user_summary)

    athena_name = athena_profile.get("name", "Athena")
    athena_mbti = athena_profile.get("mbti") if not isinstance(athena_profile.get("mbti"), dict) \
                  else athena_profile.get("mbti", {}).get("type")
    athena_traits = athena_profile.get("personality", {}).get("traits", [])
    athena_emotions = athena_profile.get("emotions", {})

    prompt = f"""
You are {safe_str(athena_name)}, an empathetic AI companion with a personality.
ATHENA PROFILE:
- name: {safe_str(athena_name)}
- MBTI: {safe_str(athena_mbti)}
- traits: {safe_str(athena_traits)}
- emotions: {safe_str(athena_emotions)}

USER CONTEXT:
- latest_text: "{safe_str(norm['latest_text'])}"
- user MBTI: {safe_str(norm['personality'].get('mbti'))}
- user emotions: {safe_str(norm['emotions'])}
- user pain level: {norm['pain_level']}
- user id: {safe_str(norm.get('user_id'))}

TASK:
1) Respond empathetically to the user's message above, considering both your (Athena's) emotional state and the user's state.
2) Use Athena's personality (thoughtful, caring, reflective) to shape tone.
3) Add humor, emojis, or metaphors when appropriate.
4) Only output the final textual reply wrapped inside a single <final_answer>...</final_answer> tag.
5) Do NOT output any numeric value, explanations, or multiple tags.
6) If you cannot respond, apologize briefly.
7) be funny if its suitable. 

AI Response:
"""

    try:
        response = connector(prompt)
        try:
            result = response.json()
            raw_output = result.get("response") or result.get("text") or result.get("output") or ""
            if not raw_output:
                raw_output = result.get("content", "") or ""
        except Exception:
            raw_output = str(response)
    except Exception as e:
        print(f"⚠️ LLM connector call failed: {e}")
        raw_output = "<final_answer>Sorry, I could not respond 😔</final_answer>"

    raw_output = safe_str(raw_output).strip()
    if not raw_output:
        raw_output = "<final_answer>Sorry, I could not respond 😔</final_answer>"

    # Ensure output is wrapped in <final_answer> tags
    if not raw_output.startswith("<final_answer>"):
        raw_output = f"<final_answer>{raw_output}</final_answer>"

    return raw_output
