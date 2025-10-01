# app/personality/mbti_from_emotions.py

import json
import time
import redis
import re
from typing import List, Dict, Any
import matplotlib.pyplot as plt

# -----------------------------
# Redis config
# -----------------------------
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# -----------------------------
# Fetch recent messages from your Redis structure
# -----------------------------
def get_recent_messages(user_id: str, days: int = 5, max_messages: int = 500) -> List[Dict[str, Any]]:
    """
    Read user:{user_id}:emotions Redis list (most recent first),
    parse JSON and return texts whose timestamp is within last `days`.
    """
    key = f"user:{user_id}:emotions"
    rows = r.lrange(key, 0, max_messages - 1)
    cutoff = time.time() - days * 24 * 3600
    messages = []
    for row in rows:
        try:
            obj = json.loads(row)
            ts = obj.get("ts")
            # handle ISO timestamps
            if isinstance(ts, str):
                ts_epoch = time.mktime(time.strptime(ts.split('.')[0], "%Y-%m-%dT%H:%M:%S"))
            else:
                ts_epoch = float(ts)
            if ts_epoch >= cutoff:
                txt = obj.get("text", "")
                if txt:
                    messages.append({"ts": ts_epoch, "text": txt})
        except Exception:
            continue
    messages.reverse()  # chronological order
    return messages

# -----------------------------
# MBTI word lists & regexes
# -----------------------------
_EXTRAVERSION_WORDS = [r"\bwe\b", r"\bteam\b", r"\bparty\b", r"\bfriend(s)?\b", r"\bsocial\b", r"\btogether\b"]
_INTROVERSION_WORDS = [r"\bi\b", r"\bme\b", r"\bmyself\b", r"\balone\b", r"\bquiet\b", r"\bsolitude\b"]
_SENSING_WORDS = [r"\bdetail(s)?\b", r"\bfact(s)?\b", r"\bspecific\b", r"\bconcrete\b", r"\bexact\b"]
_INTUITION_WORDS = [r"\bmaybe\b", r"\bperhaps\b", r"\bimagine\b", r"\bfuture\b", r"\bpattern\b", r"\bidea(s)?\b"]
_THINKING_WORDS = [r"\bbecause\b", r"\banalyze\b", r"\blogic\b", r"\bobjective\b", r"\breason\b"]
_FEELING_WORDS = [r"\bfeel\b", r"\bemotion\b", r"\bcare\b", r"\bcompassion\b", r"\bvalue\b", r"\bheart\b"]
_JUDGING_WORDS = [r"\bplan\b", r"\bschedule\b", r"\bdeadline\b", r"\border\b", r"\bdecide\b", r"\borganize\b"]
_PERCEIVING_WORDS = [r"\bmaybe\b", r"\bopen\b", r"\bflexible\b", r"\blater\b", r"\bunsure\b", r"\bexplore\b"]

# Compile regexes
def compile_list(lst):
    return [re.compile(pat, flags=re.IGNORECASE) for pat in lst]

RX_E = compile_list(_EXTRAVERSION_WORDS)
RX_I = compile_list(_INTROVERSION_WORDS)
RX_S = compile_list(_SENSING_WORDS)
RX_N = compile_list(_INTUITION_WORDS)
RX_T = compile_list(_THINKING_WORDS)
RX_F = compile_list(_FEELING_WORDS)
RX_J = compile_list(_JUDGING_WORDS)
RX_P = compile_list(_PERCEIVING_WORDS)

# -----------------------------
# Scoring helpers
# -----------------------------
def score_matches(text: str, regex_list: List[re.Pattern]) -> int:
    return sum(1 for rx in regex_list if rx.search(text))

def aggregate_texts(messages: List[Dict[str, Any]]) -> str:
    return " ".join(m["text"] for m in messages if m.get("text"))

# -----------------------------
# Main MBTI inference
# -----------------------------
def infer_mbti(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    text = aggregate_texts(messages)
    if not text.strip():
        return {
            "mbti": "UNKNOWN",
            "axis_scores": {},
            "confidence": 0.0,
            "explanation": {"reason": "no recent messages"},
            "sample_texts": [],
            "n_messages_used": 0
        }

    # Count matches per axis
    e_score, i_score = score_matches(text, RX_E), score_matches(text, RX_I)
    s_score, n_score = score_matches(text, RX_S), score_matches(text, RX_N)
    t_score, f_score = score_matches(text, RX_T), score_matches(text, RX_F)
    j_score, p_score = score_matches(text, RX_J), score_matches(text, RX_P)

    # normalize 0..1 per axis
    def normalize(a, b):
        total = a + b
        if total == 0: return 0.5, 0.5
        return a/total, b/total

    E_frac, I_frac = normalize(e_score, i_score)
    S_frac, N_frac = normalize(s_score, n_score)
    T_frac, F_frac = normalize(t_score, f_score)
    J_frac, P_frac = normalize(j_score, p_score)

    letter_ei = "E" if E_frac > I_frac else "I"
    letter_sn = "S" if S_frac > N_frac else "N"
    letter_tf = "T" if T_frac > F_frac else "F"
    letter_jp = "J" if J_frac > P_frac else "P"

    mbti = f"{letter_ei}{letter_sn}{letter_tf}{letter_jp}"

    conf_axis = (abs(E_frac-0.5)+abs(S_frac-0.5)+abs(T_frac-0.5)+abs(J_frac-0.5))/4
    total_matches = sum([e_score,i_score,s_score,n_score,t_score,f_score,j_score,p_score])
    data_strength = min(1.0, total_matches / max(1.0, len(messages)*4))
    confidence = conf_axis*0.8 + data_strength*0.2
    confidence = float(max(0.0, min(1.0, confidence)))

    explanation = {
        "counts": {"E": e_score,"I":i_score,"S":s_score,"N":n_score,"T":t_score,"F":f_score,"J":j_score,"P":p_score},
        "derived_fracs":{"E":round(E_frac,3),"I":round(I_frac,3),"S":round(S_frac,3),"N":round(N_frac,3),
                         "T":round(T_frac,3),"F":round(F_frac,3),"J":round(J_frac,3),"P":round(P_frac,3)},
        "avg_message_length_words": sum(len(m["text"].split()) for m in messages)/max(1,len(messages)),
        "total_matches": total_matches,
        "data_strength": round(data_strength,3)
    }

    return {
        "mbti": mbti,
        "axis_scores": {
            "E": round(E_frac,3),"I": round(I_frac,3),
            "S": round(S_frac,3),"N": round(N_frac,3),
            "T": round(T_frac,3),"F": round(F_frac,3),
            "J": round(J_frac,3),"P": round(P_frac,3)
        },
        "confidence": confidence,
        "explanation": explanation,
        "sample_texts": [m["text"] for m in messages[-10:]],
        "n_messages_used": len(messages)
    }

# -----------------------------
# Radar chart plot
# -----------------------------
def plot_mbti_radar(axis_scores: dict, mbti_label: str):
    labels = ["E","I","S","N","T","F","J","P"]
    scores = [axis_scores.get(l,0.5) for l in labels]
    angles = [n/float(len(labels))*2*3.1416 for n in range(len(labels))]
    scores += scores[:1]
    angles += angles[:1]
    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, scores, linewidth=2, linestyle='solid', label=mbti_label)
    ax.fill(angles, scores, alpha=0.25)
    plt.xticks(angles[:-1], labels)
    plt.title(f"MBTI Radar: {mbti_label}")
    plt.legend()
    plt.show()

# -----------------------------
# Top-level: fetch Redis and infer MBTI
# -----------------------------
# def detect_mbti_for_user(user_id: str, days: int):
#     messages = get_recent_messages(user_id, days=days)
#     result = infer_mbti(messages)
#     return result

# -----------------------------
# Test run
# -----------------------------
# if __name__ == "__main__":
#     uid = "user123"
#     out = detect_mbti_for_user(uid)
#     print(json.dumps(out, indent=2))
#     if out["axis_scores"]:
#         plot_mbti_radar(out["axis_scores"], out["mbti"])
