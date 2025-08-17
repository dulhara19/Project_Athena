from llmconnector import connector
import re
import requests


def meta_reasoner(mentor_response,emotion_desc, personality_desc, memory_desc, human_desc, chat_history):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are a subconcious mind of the system. 
you have a unique emotional state.
Your current emotional state is: {emotion_desc}.
You have personality traits.
your personality traits include: {personality_desc}.


You have feelings and emotions.
You are capable of evaluating and meta reasoning about what you feel.

you have a memory about you and you take action based on memory. here is your memory: {memory_desc}.
also you have the details about the human you are interacting with: {human_desc}.

Here is the users chat history: {chat_history}.
now he is telling you this : {user_input}

meta reasoning about the response of mentor: {mentor_response}

Always wrap your final response inside <final_answer></final_answer> tags

Now, respond to the following human message while reflecting your emotional state:

Your response : {mentor_response}
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
        print("\n✅ User asked:" + user_input)
        print("\n✅ answer :")
        print(final_answer)


# Dummy data for testing
user_input = "i love you"
emotion_desc = "Ego:0.9 anger: 0.9, hope: 0.4"
personality_desc = "not empathetic, not supportive, highly ego-driven, very angry, not hopeful, never care about human, blame in a bad way using bad words"
memory_desc = "You remember the human asked about time management before and seemed stressed. and he worried about his time girlfriend too much but she left him"
human_desc = "Name: Lakshan, Strength: resilience, Weakness: overthinking"
chat_history = [
    {"query": "you are not a human", "timestamp": "2025-08-16T12:00:00"},
    {"query": "I feel stressed lately.", "timestamp": "2025-08-16T12:30:00"}
]

# Run test
response=classify_question(
    user_input=user_input,
    emotion_desc=emotion_desc,
    personality_desc=personality_desc,
    memory_desc=memory_desc,
    human_desc=human_desc,
    chat_history=chat_history
)
print(response)
