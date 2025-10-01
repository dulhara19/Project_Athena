# app/personality/empathy_match.py
import math
from typing import Dict, Any, List
  # existing helper

# default weights (tunable)
DEFAULT_WEIGHTS = {"cognitive": 0.30, "emotional": 0.45, "motivational": 0.25}

NEGATIVE_HELP_KEYWORDS = {"help", "support", "listen", "advice", "resource"}

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def compute_desire_score(ego: Dict[str, Any]) -> float:
    """Small heuristic: returns [0..1] how much Athena wants to help."""
    score = 0.0
    if ego.get("love for the person", 0) >= 0.5:
        score += 0.6
    if ego.get("emotional_intelligence", 0) >= 0.5:
        score += 0.3
    # check if 'help' related desires or values exist
    desires = ego.get("desires", []) or []
    values = ego.get("values", []) or []
    if any("help" in str(x).lower() or "others" in str(x).lower() for x in desires + values):
        score += 0.1
    return clamp01(score)

def emotional_alignment_score(user_valence: float, athena_valence: float, strategy: str = "mirror") -> float:
    """
    user_valence, athena_valence in [-1..1].
    strategy: "mirror" (default) or "soothe" (athena tries to be opposite to calm).
    Returns 0..1 (higher = better alignment).
    """
    if strategy == "soothe":
        target = -athena_valence
    else:
        target = athena_valence
    # map absolute diff (0..2) to score (1..0)
    score = 1.0 - (abs(user_valence - target) / 2.0)
    return clamp01(score)

def cognitive_score_from_analysis(emotion_analysis: Dict[str, Any]) -> float:
    """
    Use classifier confidence and entropy / clarity of distribution.
    emotion_analysis expected shape with 'confidence' and 'emotions' dict.
    """
    conf = float(emotion_analysis.get("confidence", 0.0))
    # clarity = 1 - normalized entropy (higher when distribution peaked)
    import math
    probs = list(emotion_analysis.get("emotions", {}).values()) or []
    if not probs:
        return 0.0
    # normalize probs to sum=1 in case they don't
    s = sum(probs) or 1.0
    probs = [p / s for p in probs]
    entropy = -sum((p * math.log(p + 1e-12)) for p in probs)
    max_ent = math.log(len(probs)) if len(probs) > 1 else 1.0
    clarity = 1.0 - (entropy / (max_ent + 1e-12))
    # combine confidence and clarity
    return clamp01(0.6 * conf + 0.4 * clarity)

def empathy_match(
    user_id: str,
    ego: Dict[str, Any],
    emotion_analysis: Dict[str, Any],
    recent_texts: List[str] = None,
    strategy: str = "mirror",
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Returns:
      {
        "empathy_match": 0..1,
        "breakdown": {"cognitive":..,"emotional":..,"motivational":..},
        "recommendation": {...}
      }
    """
    from app.emotions.emotion_redis import get_recent_emotions

    if weights is None:
        weights = DEFAULT_WEIGHTS

    # cognitive
    cog = cognitive_score_from_analysis(emotion_analysis)

    # emotional: take user valence from analysis.vad.valence
    user_valence = float(emotion_analysis.get("vad", {}).get("valence", 0.0))
    # try to get athena valence from ego['happiness'] or ego['pain'] -> map to [-1..1]
    athena_val = 0.0
    if isinstance(ego.get("happiness"), dict):
        athena_val = ego.get("happiness", {}).get("level", 0.0)
    elif "happiness" in ego:
        athena_val = ego.get("happiness", 0.0)
    # note: your ego used pain/happiness in range -1..1; adjust if different
    emo = emotional_alignment_score(user_valence, athena_val, strategy=strategy)

    # motivational
    mot = compute_desire_score(ego)

    # weighted combine
    total_w = sum(weights.values())
    overall = clamp01((cog * weights["cognitive"] + emo * weights["emotional"] + mot * weights["motivational"]) / total_w)

    # recommendation: what Athena should do with empathy info
    rec = {}
    if overall >= 0.75:
        rec["tone"] = "mirror_and_engage"
        rec["suggestion"] = "Use close emotional language, reflect feelings, offer practical steps when appropriate."
    elif overall >= 0.5:
        rec["tone"] = "empathetic_probe"
        rec["suggestion"] = "Lead with empathy, ask a clarifying question, offer to help or listen."
    else:
        rec["tone"] = "cautious_support"
        rec["suggestion"] = "Prioritize emotional safety, ask simple scale question, offer resources if needed."

    # include some extra context to pass to LLM prompt
    negative_snippets = []
    if recent_texts:
        for t in recent_texts:
            tl = t.lower()
            if any(k in tl for k in ["die", "suicide", "kill myself", "i want to die", "hate you", "hate myself", "worthless"]):
                negative_snippets.append(t)
    # also include top emotion label if available
    top_label = None
    emdict = emotion_analysis.get("emotions", {})
    if emdict:
        top_label = max(emdict.items(), key=lambda x: x[1])[0]

    return {
        "empathy_match": overall,
        "breakdown": {"cognitive": round(cog, 3), "emotional": round(emo, 3), "motivational": round(mot, 3)},
        "recommendation": rec,
        "user_valence": round(user_valence, 3),
        "athena_valence": round(athena_val, 3),
        "top_emotion_label": top_label,
        "negative_snippets": negative_snippets
    }


# --------------------------------------------
# plotting the empathy match breakdown 
# --------------------------------------------

import matplotlib.pyplot as plt

def plot_empathy_match(empathy_match: dict):
    """
    Plots a bar chart of empathy match breakdown (cognitive, emotional, motivational).

    Args:
        empathy_match (dict): The empathy_match dictionary from your data
    """
    # Extract breakdown
    breakdown = empathy_match.get("breakdown", {})
    
    if not breakdown:
        print("No breakdown data available to plot.")
        return
    
    labels = list(breakdown.keys())
    values = [breakdown[label] for label in labels]

    # Create bar plot
    plt.figure(figsize=(8,5))
    bars = plt.bar(labels, values, color=["skyblue", "salmon", "limegreen"])
    plt.ylim(0, 1.0)
    plt.title("Empathy Match Breakdown")
    plt.ylabel("Matching Score")
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}", ha='center', va='bottom')
    
    plt.show()

# --------------------------------------------
# Show overall `empathy_match` score (0–1) as a speedometer-style visualization
# --------------------------------------------

import numpy as np

def plot_empathy_gauge(empathy_score):
    """
    Plots a gauge (speedometer) chart for empathy_match score.

    Parameters:
    empathy_score (float): Empathy match score between 0 and 1
    """
    if empathy_score < 0 or empathy_score > 1:
        raise ValueError("Empathy score should be between 0 and 1")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')  # Hide axes

    # Gauge settings
    theta = np.linspace(0, np.pi, 100)
    radius = 1

    # Draw background arc
    ax.plot(radius * np.cos(theta), radius * np.sin(theta), color='lightgray', linewidth=30, solid_capstyle='round')

    # Draw filled arc for empathy_score
    score_theta = np.linspace(0, np.pi * empathy_score, 100)
    ax.plot(radius * np.cos(score_theta), radius * np.sin(score_theta), color='dodgerblue', linewidth=30, solid_capstyle='round')

    # Draw pointer
    pointer_theta = np.pi * empathy_score
    ax.plot([0, 0.9 * np.cos(pointer_theta)], [0, 0.9 * np.sin(pointer_theta)], color='red', linewidth=4)

    # Add text
    ax.text(0, -0.1, f'Empathy Match: {empathy_score:.2f}', horizontalalignment='center', fontsize=14, fontweight='bold')

    plt.show()



# get recent_texts from Redis:
# recent = [m.get("text","") for m in get_recent_emotions(user_id, n=6)]
# res = empathy_match(user_id=user_id, ego=ego, emotion_analysis=emotion_data, recent_texts=recent, strategy="mirror")
