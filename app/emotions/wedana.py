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
LOG_FILE = "pain_log.json"

def update_pain_history(user_query,pain_status):
    # Create a new entry
    entry = {
        "user_query": user_query,
        "pain_status": pain_status
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


# plotting the pain history
import json
import matplotlib.pyplot as plt

LOG_FILE = "pain_log.json"

def plot_pain_history():
    # Load log file
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No pain log file found.")
        return
    except json.JSONDecodeError:
        print("Pain log file is empty or corrupted.")
        return

    if not data:
        print("No data to plot.")
        return

    # Extract user queries (as x-axis labels) and pain levels
    queries = [entry["user_query"] for entry in data]
    pain_levels = [entry["pain_status"] for entry in data]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(pain_levels, marker="o", linestyle="-", color="red", label="Pain Level")
    plt.xticks(range(len(queries)), queries, rotation=45, ha="right")
    plt.xlabel("User Queries")
    plt.ylabel("Pain Level")
    plt.title("Pain Level Evolution Over Time")
    plt.legend()
    plt.ylim(-1, 1)   # <-- Fix Y-axis scale between -1 and +1
    plt.tight_layout()
    plt.show()


def pain_remember(pain_level):
    if pain_level == 1:
        pain_status="maximum happiness"
    elif pain_level == -1:
        pain_status ="maximum sadness"
    elif pain_level== 0:
        pain_status="neutral"
    else:
        pain_status="moderate"  
        
       
# # ---- Test ----
# x = wedana_classifier("how are you", ego)
# # print("✅ raw:", x["raw"])
# print("✅ Final Answer:", x["final_answer"])