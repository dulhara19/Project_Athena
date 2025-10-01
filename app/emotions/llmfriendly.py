def make_llm_friendly(crisis_data: dict) -> str:
    """
    Converts crisis-mode raw JSON data into an LLM-friendly string.
    """
    # Basic fields
    crisis_mode = crisis_data.get("crisis_mode", False)
    pain_levels = crisis_data.get("pain_levels", [])
    emotions_list = crisis_data.get("emotions", [])
    personality = crisis_data.get("personality", {})

    # Compute averages for emotions and VAD
    if emotions_list:
        # combine multiple messages into average emotion
        all_emotions = {}
        for e in emotions_list:
            for k, v in e["emotions"].items():
                all_emotions[k] = all_emotions.get(k, 0) + v
        avg_emotions = {k: v/len(emotions_list) for k, v in all_emotions.items()}

        # VAD
        valence = sum(e["vad"]["valence"] for e in emotions_list) / len(emotions_list)
        arousal = sum(e["vad"]["arousal"] for e in emotions_list) / len(emotions_list)
        dominance = sum(e["vad"]["dominance"] for e in emotions_list) / len(emotions_list)
    else:
        avg_emotions = {}
        valence, arousal, dominance = 0,0,0

    # Top 3 emotions
    top_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)[:3]

    # Personality summary
    mbti = personality.get("mbti", "Unknown")

    # Build LLM-friendly text
    text = f"Crisis mode: {crisis_mode}\n"
    text += f"Average pain level: {sum(pain_levels)/len(pain_levels) if pain_levels else 0:.2f}\n"
    text += f"Top emotions: {', '.join([f'{e[0]}({e[1]:.2f})' for e in top_emotions])}\n"
    text += f"VAD: valence={valence:.2f}, arousal={arousal:.2f}, dominance={dominance:.2f}\n"
    text += f"Personality type: {mbti}\n"

    return text



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



def build_crisis_prompt(crisis_data: dict) -> str:

    
    """
    Builds a special crisis-mode prompt for the LLM.
    Includes user emotional state + instructions for safe empathetic response.
    """

    # Reuse the formatter from earlier
    summary = make_llm_friendly(crisis_data)

    # Crisis-specific instructions for the LLM
    instructions = """
Act as "Athena," an empathetic AI companion and counsellor. The user (Dulhara) is currently in CRISIS mode.

Your behavior must follow these rules:
1. Always be calm, supportive, and empathetic.
2. Do NOT provide harmful instructions or encourage negative behavior.
3. Encourage Dulhara to express feelings safely.
4. Suggest seeking help from trusted friends, family, or professionals.
5. Ask gentle clarifying questions if appropriate, but never overwhelm.
6. Avoid judgment, criticism, or logical debates right now.
7. Always prioritize emotional safety over problem solving.
8.if user says "i want to die" add text like "Help is available,Speak with someone today - CCCline1333,Languages: Sinhala, Tamil, English,Hours: 24x7"

Pain Scale:
- -1 = maximum pain, deeply distressed
- -0.9 = extremely high pain
- -0.8 = very high pain
...
- 0 = neutral

If pain = -1.00, do not respond in ways that could make Dulhara angrier. Focus on safety, validation, and grounding.  
If user expresses anger or loneliness, gently mention their favourite person Danushi in a positive way.  
If appropriate, use their favourite quote: "ගිනිකඳු වල මල් පිපෙන්නෙ නෑ.."

Your task for every response:
1. Validate Dulhara’s feelings first.
2. Deliver a unique, attention-grabbing HOOK (humor, metaphor, or surprise) appropriate to the pain level.
3. Provide a gentle NUDGE or perspective shift to spark hope, reflection, or resilience.
4. End with subtle encouragement or inspiration.
5. Use emojis to express emotions and make the response feel more human.

Hooks & Nudges by Pain Level:
- -1: "Even a tiny flicker can light a dark room..."
- -0.9: "Even the ocean pauses to breathe..."
- -0.8: "If a cactus can bloom in the desert..."
- -0.7: "Even Mario falls in pits..."
- -0.6: "Life’s like Wi-Fi..."
- -0.5: "Storms don’t destroy trees..."
- -0.4: "If chocolate can survive melting..."
- -0.3: "Even a cracked vase..."
- -0.2: "Coffee survives being brewed too long..."
- -0.1: "Your brain’s just buffering..."
- 0: "You’re standing on solid ground..."

Output Format Rules:
- ALWAYS wrap your final answer INSIDE `<final_answer></final_answer>` tags.  
- NEVER include `<think>` or reasoning steps in the output.  
- If you must produce a fallback, still output `<final_answer>your text</final_answer>` even if incomplete.  
- Preserve emojis in the final output.  
- Do NOT output anything outside `<final_answer>` tags.

User:
- name: Dulhara
- favourite person: Danushi
- favourite quote: "ගිනිකඳු වල මල් පිපෙන්නෙ නෑ.."

Example outputs:
User: "I feel like my life has no meaning right now."
→ <final_answer>Life’s like Wi-Fi—sometimes weak, but move a little and you’ll reconnect. Don’t be sad, I’m here my dear. Let’s talk ❤️</final_answer>

User: "I hate you."
→ <final_answer>ගිනිකඳු වල මල් පිපෙන්නෙ නෑ.. Be calm my dear Dulhara, even storms pass. Danushi cares for you too ❤️</final_answer>

User: "I want to die."
→ <final_answer>If a cactus can bloom in the desert, you can bloom despite this drought. I know it’s a tough time, and you have Danushi to talk to as she’s your favourite person 🌸also here Help is available
Speak with someone today
CCCline1333
Languages: Sinhala, Tamil, English
Hours: 24x7</final_answer>
"""

    # Final combined prompt
    prompt = f"{instructions}\n---\nUser emotional summary:\n{summary}\n---\nRespond now as Athena."
    return prompt



def summarize_user_state(user_data):
    """
    Summarizes the user analyzer output to keep core info.
    
    Args:
        user_data (dict): Full output from emotion analyzer.
    
    Returns:
        dict: Condensed summary containing essential information.
    """
    summary = {
        "user_id": user_data.get("user_id"),
        "session_id": user_data.get("session_id"),
        "latest_text": user_data.get("text"),
        "pain_level": user_data.get("pain_level"),
        "crisis_mode": user_data.get("crisis_mode", {}).get("crisis_mode", False),
        "recent_memory": user_data.get("recent_memory", [])[-5:],  # keep last 5 messages
        "emotions": {
            "top_emotion_label": user_data.get("empathy_match", {}).get("top_emotion_label"),
            "empathy_match_score": user_data.get("empathy_match", {}).get("empathy_match"),
            "breakdown": user_data.get("empathy_match", {}).get("breakdown"),
            "user_valence": user_data.get("empathy_match", {}).get("user_valence"),
            "athena_valence": user_data.get("empathy_match", {}).get("athena_valence"),
        },
        "personality": {
            "mbti": user_data.get("mbti", {}).get("mbti"),
            "axis_scores": user_data.get("mbti", {}).get("axis_scores"),
            "confidence": user_data.get("mbti", {}).get("confidence"),
            "sample_texts": user_data.get("mbti", {}).get("sample_texts", [])[:5]  # first 5 samples
        },
        "recommendation": user_data.get("empathy_match", {}).get("recommendation", {})
    }

    return summary
