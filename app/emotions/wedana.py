from app.llmconnector import connector
import re



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
-if there is no explicit content provided for classification. The user hasn't shared anything about their current emotional state or situation then give natural pain level 0.


Always wrap your final response inside <final_answer></final_answer> tags

Now, evaluate and classify the pain level of the user based on his input:

mentor response : {user_input}
AI:
"""

       # Call the connector function to get the response
    response = connector(prompt)
    result = response.json()
    raw_output = result.get("response", "")

    # Default values
    final_answer = None

    # Extract <final_answer>
    match_answer = re.search(r"<final_answer>\s*(.*?)\s*</final_answer>", raw_output, re.DOTALL | re.IGNORECASE)
    if match_answer:
        final_answer = match_answer.group(1).strip()

    return {
        "final_answer": final_answer,
        "raw": raw_output  # keep raw response for debugging
    }

# tying to implement a function to update the memory according to max sad,happy
import os,json
LOG_FILE = "memory_log.json"

def update_memory(string):
    # Create a new entry
    entry = {
        "timestamp": timestamp,
        "pain_level": pain_level
    }

    # Load existing log (if file exists), otherwise create new list
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new record
    data.append(entry)

    # Write back to file
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

    



def pain_remember(pain_level):
    if pain_level == 1:
        pain_status="maximum happiness"
    elif pain_level == -1:
        pain_status ="maximum sadness"
    update_memory        

        # (--> 1 pure happiness), (-1--> severe sad) 
       
# # ---- Test ----
# x = wedana_classifier("how are you", ego)
# # print("✅ raw:", x["raw"])
# print("✅ Final Answer:", x["final_answer"])