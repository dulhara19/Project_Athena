from llmconnector import connector
import re


ego = {
    "self esteem": 0.8,
    "age": 30,
    "city": "New York",
    "interests":["technology", "philosophy", "psychology"],
    "values": ["integrity", "empathy", "growth"],
    "strengths": ["resilience", "adaptability", "creativity"],
    "weaknesses": ["overthinking", "impatience", "self-doubt"],
    "goals": ["personal growth", "helping others", "finding purpose"],
    "fears": ["failure", "rejection", "loneliness"],
    "dreams": ["making a difference", "leaving a legacy", "finding true happiness"],
    "memories": ["graduation day", "first job", "traveling abroad"],
    "beliefs": ["everyone has potential", "failure is a learning opportunity", "kindness matters"],
    "emotions": { "happiness": 0.5, "anger": 0.2, "fear": 0.1 },
    "personality": {
        "traits": ["empathetic", "curious", "analytical"],
        "communication_style": "thoughtful and reflective",
        "decision_making": "careful and deliberate"
    }
}


def wedana_classifier(user_input,ego):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are a classifier of pain levels based on user input.
You have to classify the pain level of the user based on his input. 

you have ego about you. here is your ego: {ego}.
now the user is telling you this : {user_input}
You have to classify your pain level of the user based on his input.
pain level vary from -1 to 1.
-1 means very strong pain(sadness) level and 1 means very positive happiness pain level.
and 0 means neutral pain level.

your job is to classify the pain level of the user based on his input.

-when user is telling you something which negatively corelated to your {ego}, consider it as a sadness. 
-when user is telling you something which positively corelated to your {ego}, consider it as a happiness.
-based return a pain level between -1 to 1.


Always wrap your final response inside <final_answer></final_answer> tags

Now, evaluate and meta reason to the following mentor response message:

mentor response : {mentor_response}
AI:
"""

    # Call the connector function to get the response
    # Send request to LLM
    response = connector(prompt)

    # Parse and extract classification
    result = response.json()
    raw_output = result.get("response", "")

    # debugging---
    # Print raw output for debugging
    # print("\n✅ Raw LLM Output:\n", raw_output)

    # Extract <final_answer>
    match = re.search(r"<final_answer>\s*(.*?)\s*</final_answer>", raw_output, re.DOTALL | re.IGNORECASE)

    if match:
        final_answer = match.group(1).strip()
        
        # print(final_answer)
        return final_answer




def calculate_pain(level):
    if not (1 <= level <= 10):
        return "Invalid pain level. Please enter a number between 1 and 10."
    
    if 1 <= level <= 3:
        return "mild"
    elif 4 <= level <= 6:
        return "moderate"
    else:
        return "severe"

# Example usage:
print(calculate_pain(2))  # mild
print(calculate_pain(5))  # moderate
print(calculate_pain(9))  # severe


# option 2

# def calculate_pain(category):
#     category = category.lower()
#     if category == "mild":
#         return "Pain level: 1-3"
#     elif category == "moderate":
#         return "Pain level: 4-6"
#     elif category == "severe":
#         return "Pain level: 7-10"
#     else:
#         return "Invalid category. Choose mild, moderate, or severe."

# # Example usage:
# print(calculate_pain("mild"))

