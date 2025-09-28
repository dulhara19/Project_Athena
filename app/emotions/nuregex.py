import re
from typing import Tuple, Optional

NUM_RE = re.compile(r"[-+]?\d*\.\d+|[-+]?\d+")  # matches floats and ints
WELL_FORMED_TAG_RE = re.compile(r"<final_answer>\s*([-+]?\d*\.?\d+|\d+)\s*</final_answer>", re.IGNORECASE)
OPEN_TAG_CONTENT_RE = re.compile(r"<final_answer(?:\s[^>]*)?>\s*([^<\n\r]+)", re.IGNORECASE)
TAG_LIKE_RE = re.compile(r"(?:<\s*\/?\s*final(?:_answer)?\s*[^>]*>|final_answer|final)[^0-9\.\-+]{0,20}", re.IGNORECASE)

def extract_pain_level(raw: str, fallback: float = 0.0) -> Tuple[float, dict]:
    """
    Extract a pain level from messy LLM output.
    Returns (value, debug_info).
    debug_info contains 'method', 'candidates', 'raw'.
    """
    debug = {"raw": raw, "method": None, "candidates": []}

    if not raw:
        debug["method"] = "empty"
        return float(fallback), debug

    # 1) exact well-formed tag
    m = WELL_FORMED_TAG_RE.search(raw)
    if m:
        val = float(m.group(1))
        val = max(-1.0, min(1.0, val))
        debug["method"] = "well_formed_tag"
        debug["candidates"] = [m.group(1)]
        return val, debug

    # 2) open tag capture: <final_answer ...>some text...
    m2 = OPEN_TAG_CONTENT_RE.search(raw)
    if m2:
        text = m2.group(1).strip()
        # try to find first numeric token inside that capture
        num_m = NUM_RE.search(text)
        if num_m:
            val = float(num_m.group(0))
            val = max(-1.0, min(1.0, val))
            debug["method"] = "open_tag_content"
            debug["candidates"] = [num_m.group(0)]
            return val, debug
        # if no numeric inside, fall through to proximity method but record capture
        debug["candidates"].append(text)

    # 3) search for tag-like tokens and extract nearest numeric token for each occurrence
    # We'll scan every 'final' occurrence and look +/- N chars for numbers
    proximity_candidates = []
    for mtag in re.finditer(r"(final_answer|final|<final_answer|</final_answer|</final>)", raw, re.IGNORECASE):
        start, end = mtag.span()
        # context window (chars) to search for numbers around the tag
        window_left = max(0, start - 40)
        window_right = min(len(raw), end + 40)
        window = raw[window_left:window_right]
        nums = NUM_RE.findall(window)
        if nums:
            # pick the numeric token closest to the tag center
            # compute distances (distance from tag center to each match)
            center = (start + end) // 2
            best = None
            best_dist = None
            for n_match in NUM_RE.finditer(window):
                # compute absolute char distance from tag center
                match_start = window_left + n_match.start()
                dist = abs(match_start - center)
                if best is None or dist < best_dist:
                    best = n_match.group(0)
                    best_dist = dist
            if best is not None:
                proximity_candidates.append(best)

    if proximity_candidates:
        # prefer the last proximity candidate (often model prints multiple, last is intended)
        chosen = proximity_candidates[-1]
        try:
            val = float(chosen)
            val = max(-1.0, min(1.0, val))
            debug["method"] = "proximity_to_tag"
            debug["candidates"] = proximity_candidates
            return val, debug
        except Exception:
            pass

    # 4) fallback: take the last numeric token in entire raw text (safe heuristic)
    all_nums = NUM_RE.findall(raw)
    if all_nums:
        chosen = all_nums[-1]
        try:
            val = float(chosen)
            val = max(-1.0, min(1.0, val))
            debug["method"] = "last_numeric_token"
            debug["candidates"] = all_nums
            return val, debug
        except Exception:
            pass

    # 5) ultimate fallback: return default
    debug["method"] = "fallback"
    debug["candidates"] = []
    return float(fallback), debug


# -------------------------
# quick examples / tests
if __name__ == "__main__":
    examples = [
        "<0final_answer>-1</final>, <final_answer>0</final>0</final>, final_answer>0</final>0</final> <final_answer>0</final_answer>0</final>",
        "Final answer should be0. Need wrap in tags. </think>\n<final_answer>0</final>0</final>",
        "<final_answer>0.6</final_answer>",
        "nothing here",
        "some text final_answer: -0.3 and more text"
    ]
    for ex in examples:
        val, dbg = extract_pain_level(ex)
        print("RAW:", ex)
        print("-> value:", val, "method:", dbg["method"], "candidates:", dbg["candidates"])
        print("-" * 60)
