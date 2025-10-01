# app/personality/correlation.py
import json
from typing import Dict, Any, List, Optional
from collections import Counter

# Optional semantic similarity (install sentence-transformers to enable)
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    _HAS_EMBED = True
    _EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _HAS_EMBED = False
    _EMB_MODEL = None

# Import your existing project helpers
# - detect_mbti_for_user from your MBTI module (reads Redis as we designed)
# - get_recent_emotions from emotion_redis (reads Redis list user:{user_id}:emotions)
from app.emotions.mbti import detect_mbti_for_user
from app.emotions.emotion_redis import get_recent_emotions

# ---------- Utilities ----------
def jaccard_similarity(a: List[str], b: List[str]) -> float:
    if not a and not b:
        return 0.0
    sa, sb = set(x.lower() for x in a), set(x.lower() for x in b)
    if not sa and not sb:
        return 0.0
    inter = sa.intersection(sb)
    union = sa.union(sb)
    return len(inter) / len(union)

def embedding_similarity(texts_a: List[str], texts_b: List[str]) -> float:
    if not _HAS_EMBED or not _EMB_MODEL:
        return 0.0
    a = " ".join(texts_a) if isinstance(texts_a, list) else str(texts_a)
    b = " ".join(texts_b) if isinstance(texts_b, list) else str(texts_b)
    emb_a = _EMB_MODEL.encode(a, convert_to_tensor=True)
    emb_b = _EMB_MODEL.encode(b, convert_to_tensor=True)
    sim = float(st_util.cos_sim(emb_a, emb_b).item())
    return (sim + 1.0) / 2.0  # map from [-1,1] to [0,1]

# MBTI axis similarity (expects axis dicts with fractions for letters, 0..1)
def mbti_axis_similarity(user_axis: Dict[str, float], athena_axis: Dict[str, float]) -> float:
    axes = [("E","I"), ("S","N"), ("T","F"), ("J","P")]
    dsum = 0.0
    for left, right in axes:
        u_left = user_axis.get(left, 0.5)
        u_right = user_axis.get(right, 0.5)
        a_left = athena_axis.get(left, 0.5)
        a_right = athena_axis.get(right, 0.5)
        # axis scalar in [-1..1]
        u_scalar = u_left - u_right
        a_scalar = a_left - a_right
        d = abs(u_scalar - a_scalar) / 2.0  # normalized to [0..1]
        dsum += d
    avg_dist = dsum / 4.0
    return max(0.0, 1.0 - avg_dist)

def sentiment_alignment(user_valence: float, athena_happiness: float) -> float:
    # user_valence, athena_happiness in [-1..1]
    if abs(user_valence) < 0.05 and abs(athena_happiness) < 0.05:
        return 1.0
    if user_valence * athena_happiness >= 0:
        return max(0.0, 1.0 - (abs(user_valence - athena_happiness) / 2.0))
    else:
        return max(0.0, 1.0 - (abs(user_valence) + abs(athena_happiness)) / 2.0)

def value_interest_similarity(user_texts: List[str], athena_values: List[str], athena_interests: List[str]) -> float:
    tokens = Counter()
    for t in user_texts:
        for w in t.lower().split():
            w = "".join(ch for ch in w if ch.isalnum())
            if len(w) > 2:
                tokens[w] += 1
    user_keywords = set(tokens.keys())
    values = set(v.lower() for v in (athena_values or []))
    interests = set(i.lower() for i in (athena_interests or []))
    vmatch = (len(user_keywords.intersection(values)) / max(1, len(values))) if values else 0.0
    imatch = (len(user_keywords.intersection(interests)) / max(1, len(interests))) if interests else 0.0
    return (vmatch + imatch) / 2.0

# ---------- Main correlation function ----------
def correlate_user_with_athena(
    user_id: str,
    athena_ego: Dict[str, Any],
    user_mbti_result: Optional[Dict[str, Any]] = None,
    recent_texts: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Compute compatibility between user and Athena.
    Returns:
      {
        overall_score: 0..1,
        breakdown: {mbti, traits, values, sentiment, embed},
        recommendation: {tone, actions, suggested_topics},
        user_mbti: {...},
        recent_texts: [...]
      }
    """
    if weights is None:
        weights = {"mbti": 0.35, "traits": 0.15, "values": 0.2, "sentiment": 0.15, "embed": 0.15}

    # 1) user MBTI (from Redis) if not passed in
    if user_mbti_result is None:
        user_mbti_result = detect_mbti_for_user(user_id, days=5)
    user_axis = user_mbti_result.get("axis_scores", {})

    # 2) recent_texts: from Redis if not given
    if recent_texts is None:
        recent_msgs = get_recent_emotions(user_id, n=8)  # most recent 8
        recent_texts = [m.get("text","") for m in recent_msgs]

    # 3) Athena MBTI axis build (from ego.personality_type if available)
    athena_axis = {"E":0.5,"I":0.5,"S":0.5,"N":0.5,"T":0.5,"F":0.5,"J":0.5,"P":0.5}
    athena_mbti = athena_ego.get("personality_type")
    if isinstance(athena_mbti, str) and len(athena_mbti) == 4:
        # deterministic one-hot-like mapping
        a = athena_mbti.upper()
        def axis_frac(letter, left, right):
            return (1.0 if letter==left else 0.0, 1.0 if letter==right else 0.0)
        eleft, eright = axis_frac(a[0], "E", "I"); athena_axis["E"]=eleft; athena_axis["I"]=eright
        sleft, sright = axis_frac(a[1], "S", "N"); athena_axis["S"]=sleft; athena_axis["N"]=sright
        tleft, tright = axis_frac(a[2], "T", "F"); athena_axis["T"]=tleft; athena_axis["F"]=tright
        jleft, jright = axis_frac(a[3], "J", "P"); athena_axis["J"]=jleft; athena_axis["P"]=jright

    # 4) MBTI similarity
    mbti_sim = mbti_axis_similarity(user_axis, athena_axis)

    # 5) Trait overlap (use user_mbti_result MBTI as quick trait + simple keywords)
    user_traits = []
    if user_mbti_result and user_mbti_result.get("mbti") and user_mbti_result.get("confidence",0) > 0.2:
        user_traits.append(user_mbti_result.get("mbti"))
    # simple extraction: pick human words that hint traits
    words = set(w.lower().strip(".,!?") for t in recent_texts for w in t.split() if len(w)>2)
    if any(x in words for x in ["help","care","support","empathetic","kind"]):
        user_traits.append("empathetic")
    if any(x in words for x in ["plan","goal","organize","schedule","deadline"]):
        user_traits.append("organized")
    athena_traits = athena_ego.get("personality", {}).get("traits", []) or athena_ego.get("traits", [])
    traits_sim = jaccard_similarity(user_traits, athena_traits or [])

    # 6) Values/interests similarity
    values_sim = value_interest_similarity(recent_texts, athena_ego.get("values", []), athena_ego.get("interests", []))

    # 7) Sentiment alignment: get latest valence from Redis if available
    latest = get_recent_emotions(user_id, n=1)
    user_valence = 0.0
    if latest:
        user_valence = latest[0].get("emotion", {}).get("vad", {}).get("valence", 0.0)
    athena_happiness = 0.0
    if isinstance(athena_ego.get("happiness"), dict):
        athena_happiness = athena_ego.get("happiness", {}).get("level", 0.0)
    else:
        athena_happiness = float(athena_ego.get("happiness") or 0.0)
    sentiment_sim = sentiment_alignment(user_valence, athena_happiness)

    # 8) Embedding similarity (optional)
    emb_sim = 0.0
    if _HAS_EMBED:
        athena_profile_text = " ".join(map(str, (athena_ego.get("values",[])+athena_ego.get("interests",[])+athena_traits+athena_ego.get("memories",[]))))
        emb_sim = embedding_similarity(recent_texts, [athena_profile_text])

    # 9) Combine breakdown and overall score
    breakdown = {"mbti": mbti_sim, "traits": traits_sim, "values": values_sim, "sentiment": sentiment_sim, "embed": emb_sim}
    total_w = sum(weights.values())
    overall = 0.0
    for k,w in weights.items():
        overall += breakdown.get(k, 0.0) * (w / total_w)
    overall = float(max(0.0, min(1.0, overall)))

    # 10) Recommendations
    if overall > 0.75:
        tone = "mirror"
        tone_text = "Friendly & aligned — match user's tone and mirror language."
    elif overall > 0.5:
        tone = "adapt"
        tone_text = "Supportive — adapt to user's style and gently guide."
    else:
        tone = "cautious"
        tone_text = "Cautious — ask clarifying questions, focus on emotional safety."

    rec = {
        "tone": tone,
        "tone_text": tone_text,
        "actions": ["mirror"] if tone=="mirror" else (["probe"] if tone=="adapt" else ["ask_clarify"]),
        "suggested_topics": list(dict.fromkeys(athena_ego.get("interests", [])[:3]))  # unique order-preserved
    }

    return {
        "overall_score": overall,
        "breakdown": breakdown,
        "recommendation": rec,
        "user_mbti": user_mbti_result,
        "recent_texts": recent_texts
    }

# ---------- quick example runner ----------
# if __name__ == "__main__":
#     # Example Athena ego (replace with your real ego import)
#     ego = {
#         "personality_type": "INTJ",
#         "personality": {"traits":["empathetic","curious","analytical"]},
#         "values": ["integrity","empathy"],
#         "interests": ["technology","philosophy"]
#     }
#     res = correlate_user_with_athena("user123", ego)
#     print(json.dumps(res, indent=2))


