import math

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

def sign_with_zero(x):
    # treat very small numbers as zero
    if x is None:
        return 0
    x = float(x)
    if abs(x) < 1e-6:
        return 0
    return 1 if x > 0 else -1

def empathy_from_pain(
    athena_pain: float,
    user_pain: float,
    *,
    confidence: float = 0.0,
    weights: dict = None,
    soothe_mode: bool = False
) -> dict:
    """
    Compute a quick empathy metric from Athena's pain and user's pain.
    - athena_pain, user_pain: floats in [-1, 1] (-1 sad -> +1 happy)
    - confidence: optional classifier confidence (0..1) to nudge score
    - weights: optional dict of weights for components {"align":0.7,"dir":0.2,"conf":0.1}
    - soothe_mode: if True, treat opposite sign (Athena intentionally soothes) as positive
    Returns dict with:
      {
        "empathy": 0..1,
        "alignment": 0..1,         # based on absolute difference
        "same_direction": 0 or 1,  # 1 if signs equal or one is zero
        "raw_diff": float,         # abs difference between pains (0..2)
        "confidence": confidence,
        "components": {...}
      }
    """
    # default weights
    if weights is None:
        weights = {"align": 0.7, "dir": 0.2, "conf": 0.1}

    # sanitize inputs
    try:
        a = float(athena_pain)
    except Exception:
        a = 0.0
    try:
        u = float(user_pain)
    except Exception:
        u = 0.0
    conf = float(confidence) if confidence is not None else 0.0
    conf = max(0.0, min(1.0, conf))

    # raw absolute difference [0..2]
    raw_diff = abs(a - u)   # max difference: |1 - (-1)| = 2

    # alignment: map diff [0..2] -> [1..0] where diff=0 => 1.0, diff=2 => 0.0
    alignment = 1.0 - (raw_diff / 2.0)
    alignment = clamp01(alignment)

    # same sign flag (treat zero as neutral)
    s_a = sign_with_zero(a)
    s_u = sign_with_zero(u)
    same_direction = 1 if (s_a == s_u or s_a == 0 or s_u == 0) else 0

    # if soothe_mode is True, opposite signs may be desirable:
    if soothe_mode and s_a != 0 and s_u != 0 and s_a != s_u:
        # reward some opposite-sign behavior as soothing:
        # compute soothing bonus based on magnitude difference but cap it
        soothe_bonus = clamp01(0.5 * (abs(a) + abs(u)) / 2.0)  # 0..0.5
        # treat same_direction as softened
        same_direction_component = 0.5  # partial credit when opposite but intended
    else:
        soothe_bonus = 0.0
        same_direction_component = float(same_direction)

    # combine components
    w_align = weights.get("align", 0.7)
    w_dir = weights.get("dir", 0.2)
    w_conf = weights.get("conf", 0.1)
    total_w = w_align + w_dir + w_conf

    # effective direction score
    dir_score = same_direction_component

    raw_emp = (w_align * alignment + w_dir * dir_score + w_conf * conf) / total_w
    raw_emp = clamp01(raw_emp + soothe_bonus)

    return {
        "empathy": round(raw_emp, 3),
        "alignment": round(alignment, 3),
        "same_direction": int(same_direction),
        "raw_diff": round(raw_diff, 3),
        "confidence": round(conf, 3),
        "components": {
            "w_align": w_align, "w_dir": w_dir, "w_conf": w_conf,
            "soothe_bonus": round(soothe_bonus, 3)
        }
    }
import matplotlib.pyplot as plt

def plot_eval(athena_pain, user_pain):
    labels = ['Athena','User']
    vals = [athena_pain, user_pain]
    fig, ax = plt.subplots(figsize=(4,3))
    ax.bar(labels, vals, color=['#2a9d8f','#e76f51'])
    ax.set_ylim(-1,1)
    ax.axhline(0,color='gray',linewidth=0.5)
    ax.set_ylabel('pain (-1 sad -> +1 happy)')
    plt.show()
