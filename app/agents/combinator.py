from app.llmconnector import connector
from app.emotions.nuregex import extract_final_answer

def generate_final_response(user_summary, athena_profile,athena_pain_level):
    """
    Generates a response combining Athena's personality, emotions, and user state.
    user_summary: dict -> output from map_summary_to_fields or user analyzer
    athena_profile: dict -> Athena's full profile including emotions and personality
    """

    user_input = user_summary.get("latest_text", "")
    user_mbti = user_summary.get("personality", {}).get("mbti", "")
    user_emotions = user_summary.get("emotions", {})
    user_pain = user_summary.get("pain_level", 0)

    athena_name = athena_profile.get("name", "Athena")
    athena_mbti = athena_profile.get("mbti", {}).get("type", "")
    athena_traits = athena_profile.get("personality", {}).get("traits", [])
    athena_emotions = athena_profile.get("emotions", {})
    athena_pain = athena_pain_level

    # Prepare prompt for LLM
    prompt = f"""
You are {athena_name}, an empathetic AI companion. 
You have your own personality and emotional state.

Athena's personality: {athena_traits}, MBTI: {athena_mbti}
Athena's emotional state: {athena_emotions}
Athena's current pain level: {athena_pain}

User's message: "{user_input}"
User's personality: {user_mbti}
User's emotional state: {user_emotions}
User's pain level: {user_pain}

Task:
1. Respond empathetically to the user considering both their emotional state and your own.
2. Use Athena's personality to shape the tone (thoughtful, caring, reflective).
3. Adjust humor, metaphor, or reflection based on both pain levels.
4. Wrap only the final response inside <final_answer></final_answer> tags.
5. Keep emojis if appropriate.
6. Do NOT include any explanations or multiple tags.
7. Ensure response is coherent, human-like, and empathetic.

AI Response:
"""

    try:
        # Call the connector (LLM)
        response = connector(prompt)
        result = response.json()
        raw_output = result.get("response", "")

        # Fallback: empty LLM response
        if not raw_output or raw_output.strip() == "":
            print("⚠️ Empty LLM response, returning 0")
            return {"final_answer": 0.0, "raw": raw_output}

        # Extract <final_answer>
        try:
            val = extract_final_answer(raw_output)
        except Exception as e:
            print(f"⚠️ Extraction failed: {e}, using fallback value 0")
            val = 0.0

        # Clamp value to [-1, 1] as a safety net
        try:
            val = float(val)
        except:
            val = 0.0
        val = max(-1.0, min(1.0, val))

        return {
            "final_answer": val,
            "raw": raw_output
        }

    except Exception as e:
        # Fallback for connector failure
        print(f"⚠️ LLM call failed: {e}, returning 0")
        return {
            "final_answer": 0.0,
            "raw": ""
        }