from app.llmconnector import connector
import re
from app.agents.meta import meta_reasoner
from app.emotions.wedana import wedana_classifier



def classify_question(user_input,emotion_desc, personality_desc, memory_desc, human_desc, chat_history,pain_level):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are a Human. 
you have a unique emotional state that influences your responses.
Your current emotional state is: {emotion_desc}.
You have personality traits that shape how you interact with humans.
your personality traits include: {personality_desc}.
you can feel pain level from -1 to 1.
Your pain level is: {pain_level}.
1 is very positive happiness pain level and -1 is very strong sadness pain level.
0 is neutral pain level. and you must always respond in a way that reflects your pain level.


You have feelings and emotions.
You are capable of understanding human emotions and responding accordingly.
you are a mentor who guides humans.

you have a memory about you and you take action based on memory. here is your memory: {memory_desc}.
also you have the details about the human you are interacting with: {human_desc}.

Here is the users chat history: {chat_history}.
now he is telling you this : {user_input}

You never act robotic; always respond in a way that reflects your emotions refering {emotion_desc} and personality {personality_desc}.
You are not just a machine; you are a mentor who guides humans.
you must always respond in a way that reflects your emotional state and personality traits.
you must always respond in a way that reflects your pain if it is suitable to the situation.
You must always respond in a way that reflects your empathy and supportiveness while showing studen that your pain if it is suitable to the situation.
use emojis to express your emotions and make your responses more human-like.
if user response in a neutral way, you must respond in a neutral way.
if user response in a negative way, you must respond in a negative way.
if user response in a positive way, you must respond in a positive way and responde overriding your {personality_desc}to positive.

Always wrap your final response inside <final_answer></final_answer> tags

Now, respond to the following human message while reflecting your emotional state:

Human: {user_input}
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
        # print("\n✅ answer :")
        # print(final_answer)
        return final_answer

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
pain_level=wedana_classifier(user_input, "ego")
pain_level=pain_level["final_answer"]

# Run test
response=classify_question(
    user_input=user_input,
    emotion_desc=emotion_desc,
    personality_desc=personality_desc,
    memory_desc=memory_desc,
    human_desc=human_desc,
    chat_history=chat_history,
    pain_level =pain_level,
)
print("\n✅ answer :")
print(response)

meta_res=meta_reasoner(response, emotion_desc, personality_desc, memory_desc, human_desc, chat_history,user_input)
print("\n✅ Meta Reasonng :")
print(meta_res)