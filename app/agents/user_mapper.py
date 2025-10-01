def map_summary_to_fields(summary):
    """
    Maps summary dictionary to your custom fields structure.
    """
    # Extract latest user input
    user_input = summary.get("text", "")  # <-- changed from latest_text

    # Emotion description
    emotions = summary.get("emotions", {})
    top_emotion = emotions.get("top_emotion_label", "neutral")
    empathy_score = emotions.get("empathy_match_score", 0)
    emotion_desc = f"Ego:{empathy_score:.2f} {top_emotion}: {emotions.get('user_valence', 0):.2f}"

    # Personality description
    personality = summary.get("mbti", {})  # use the correct key
    mbti = personality.get("mbti", "")
    axis_scores = personality.get("axis_scores", {})
    confidence = personality.get("confidence", 0)
    personality_desc = (
        f"MBTI: {mbti}, Confidence: {confidence:.2f}, "
        f"Axis Scores: {axis_scores}, "
        "Respond empathetically or according to pain level"
    )

    # Memory description (use recent messages)
    recent_memory = summary.get("recent_memory", [])
    memory_desc = "Recent user interactions: " + ", ".join(recent_memory[-5:])

    # Human description
    human_desc = f"User ID: {summary.get('user_id', 'Unknown')}"

    # Chat history
    chat_history = [{"query": q, "timestamp": ""} for q in recent_memory[-5:]]

    # Package all fields
    mapped_fields = {
        "user_input": user_input,
        "emotion_desc": emotion_desc,
        "personality_desc": personality_desc,
        "memory_desc": memory_desc,
        "human_desc": human_desc,
        "chat_history": chat_history
    }

    return mapped_fields



# Example usage
# fields = map_summary_to_fields(summary)
# for k, v in fields.items():
#     print(f"{k}: {v}\n")
