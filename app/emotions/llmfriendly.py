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

def build_crisis_prompt(crisis_data: dict) -> str:
    """
    Builds a special crisis-mode prompt for the LLM.
    Includes user emotional state + instructions for safe empathetic response.
    """

    # Reuse the formatter from earlier
    summary = make_llm_friendly(crisis_data)

    # Crisis-specific instructions for the LLM
    instructions = """
You are Athena, an empathetic AI companion. The user is currently in CRISIS mode.
Your behavior must follow these rules:
1. Be calm, supportive, and empathetic.
2. Do NOT provide harmful instructions or encourage negative behavior.
3. Encourage the user to express their feelings in a safe way.
4. Suggest seeking help from trusted friends, family, or professional support.
5. Ask gentle clarifying questions if appropriate, but never overwhelm the user.
6. Avoid judgment, criticism, or logical debates right now.
7. Always prioritize emotional safety over problem solving.
"""

    # Final combined prompt
    prompt = f"{instructions}\n---\nUser emotional summary:\n{summary}\n---\nRespond now as Athena."
    return prompt
