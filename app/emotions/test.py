import re
from typing import Optional

# --- helper cleaners ---
def _strip_surrounding_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1].strip()
    return s

def _remove_trailing_tags(s: str) -> str:
    # remove a trailing partial closing tag like </final> or stray '<final>' at edges
    s = re.sub(r'^\s*<[^>]{1,50}>\s*', '', s)   # leading single tag
    s = re.sub(r'\s*<\s*/\s*[^>]{1,50}>\s*$', '', s)  # trailing closing tag
    return s

def _clean_text(s: str) -> str:
    # collapse multiple whitespace, strip leading/trailing, remove weird multiple newlines
    s = s.replace('\r', ' ')
    s = re.sub(r'\s+\n', '\n', s)
    s = re.sub(r'\n{2,}', '\n', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    s = s.strip()
    # remove surrounding quotes if present
    s = _strip_surrounding_quotes(s)
    # remove simple wrapping tags at edges
    s = _remove_trailing_tags(s)
    return s.strip()

# --- main extractor ---
def extract_final_answer_v2(text: str) -> str:
    """
    Robustly extract the final answer string from LLM output.

    Priority order:
      1) If a </think> tag exists, return everything after the LAST </think>.
      2) Else, return content of the LAST matched tag among <final_answer>, <final>, <answer>.
      3) Else, return content after the last prefix like 'Final response:', 'Final answer:', or 'Answer -'.
      4) Else, return the last non-empty chunk of text (cleaned).

    Always returns a cleaned plain string (no surrounding tags).
    """
    if not isinstance(text, str):
        return ""

    # normalize
    full = text

    # 1) prefer content after the last </think> tag (case-insensitive)
    think_iter = list(re.finditer(r'</\s*think\s*>', full, flags=re.IGNORECASE))
    if think_iter:
        last_think = think_iter[-1]
        after = full[last_think.end():].strip()
        if after:
            # clean up and return
            cleaned = _clean_text(after)
            if cleaned:
                return cleaned

    # 2) try to find the last well-formed tag among candidate tags
    tag_names = ["final_answer", "final", "answer"]
    # pattern finds <tag> ... </tag> non-greedy, case-insensitive
    pattern_tags = re.compile(r'<\s*({tags})\s*>\s*([\s\S]*?)\s*<\s*/\s*\1\s*>'.format(tags="|".join(tag_names)),
                              flags=re.IGNORECASE)
    matches = list(pattern_tags.finditer(full))
    if matches:
        last = matches[-1]
        inner = last.group(2)
        cleaned = _clean_text(inner)
        if cleaned:
            return cleaned

    # 3) prefix style search (look for last occurrence)
    prefix_patterns = [
        r'(?:Final answer|Final response|Final response:|Final|Answer)\s*[:\-]\s*["\']?(.*?)["\']?\s*$',
        r'(?:Final answer|Final response|Final|Answer)\s*\:\s*["\']?(.*?)["\']?(?:\n|$)',
    ]
    # try scanning from the end: reverse the lines and search
    lines = [ln.strip() for ln in full.splitlines() if ln.strip()]
    # search lines from last to first
    for ln in reversed(lines):
        for pat in prefix_patterns:
            m = re.search(pat, ln, flags=re.IGNORECASE)
            if m:
                cleaned = _clean_text(m.group(1))
                if cleaned:
                    return cleaned

    # also try searching the whole text for a prefix (last match)
    prefix_re = re.compile(r'(?:Final answer|Final response|Answer)\s*[:\-]\s*["\']?(.*?)["\']?(?:\n|$)', flags=re.IGNORECASE | re.DOTALL)
    all_pref = list(prefix_re.finditer(full))
    if all_pref:
        last_pref = all_pref[-1].group(1)
        cleaned = _clean_text(last_pref)
        if cleaned:
            return cleaned

    # 4) fallback: try to extract the last non-empty paragraph (split by blank lines)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', full) if p.strip()]
    if paragraphs:
        candidate = paragraphs[-1]
        cleaned = _clean_text(candidate)
        if cleaned:
            return cleaned

    # final fallback: return the whole cleaned text
    return _clean_text(full)
