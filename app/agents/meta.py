from app.llmconnector import connector
import re
import requests


def meta_reasoner(mentor_response,emotion_desc, personality_desc, memory_desc, human_desc, chat_history,user_input):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are a subconcious mind of the mentor. 
mentor has unique emotional state.
mentor's current emotional state is: {emotion_desc}.
mentor has personality traits.
mentor's personality traits include: {personality_desc}.


mentor have feelings and emotions.
You as the subconcious mide of the mentor you are capable of evaluating and meta reasoning about what mentor is feeing.

you have a memory about mentor and mentor takes action based on his memory. here is mentor's memory: {memory_desc}.
also you have the details about the human that mentor is interacting with: {human_desc}.

Here is the users chat history: {chat_history}.
now currectly he is telling to the mentor about this : {user_input}
this was the response of mentor: {mentor_response}

you have to meta reasoning about the response of mentor: {mentor_response}

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


