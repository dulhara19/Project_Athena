# agent_memory = {
#     "user_profile": {
#         "name": "Lakshan",
#         "age": 23,
#         "goals": ["learn AI", "become millionaire"]
#     },
#     "emotional_traits": {
#         "strengths": ["hardworking", "curious"],
#         "weaknesses": ["impatient"],
#         "attitudes": ["positive"]
#     },
#     "chat_history": []
# }

# # update profile dynamically
# agent_memory["user_profile"]["age"] = 24  
# agent_memory["emotional_traits"]["weaknesses"].append("self-doubt")
# agent_memory["chat_history"].append("User asked about LinkedIn post")

import datetime

# our data structure (global or inside your agent memory dict)
pain_history = []

def update_agent_pain(pain_level: float):
    """Append pain level with timestamp to the history list"""
    timestamp = datetime.datetime.now()
    pain_history.append((timestamp, pain_level))
    print(f"✅ Recorded pain level {pain_level} at {timestamp}")
    return pain_history


# Example usage




#plotting the pain history
import matplotlib.pyplot as plt

def plot_pain_history(pain_history):
    if not pain_history:
        print("No data to plot yet.")
        return
    
    # separate timestamps and pain levels
    times = [t for t, _ in pain_history]
    levels = [p for _, p in pain_history]

    # plot
    plt.figure(figsize=(8, 4))
    plt.plot(times, levels, marker="o", linestyle="-", color="red")
    plt.xlabel("Time")
    plt.ylabel("Pain Level")
    plt.title("Pain Evolution Over Time")
    plt.xticks(rotation=45)  # tilt timestamps so they don’t overlap
    plt.grid(True)
    plt.tight_layout()
    plt.show()



# plot_pain_history(pain_history)

# def update_agent_memory(memory, section, key=None, value=None, append=False):
#     """
#     Dynamically update agent memory.
#     - section: which part ("user_profile", "emotional_traits", "chat_history")
#     - key: field to update inside section (optional)
#     - value: new value
#     - append: if True, appends instead of replacing
#     """

#     if section not in memory:
#         memory[section] = {} if key else []

#     if key:
#         if append and isinstance(memory[section].get(key), list):
#             memory[section][key].append(value)
#         else:
#             memory[section][key] = value
#     else:
#         # no key → directly append or set whole section
#         if append and isinstance(memory[section], list):
#             memory[section].append(value)
#         else:
#             memory[section] = value

#     return memory

# agent_memory = {
#     "user_profile": {"name": "Lakshan"},
#     "emotional_traits": {"strengths": [], "weaknesses": []},
#     "chat_history": []
# }

# # Update user age
# update_agent_memory(agent_memory, "user_profile", "age", 24)

# # Add a strength
# update_agent_memory(agent_memory, "emotional_traits", "strengths", "resilient", append=True)

# # Add chat history
# update_agent_memory(agent_memory, "chat_history", value="Asked about agent design", append=True)

# print(agent_memory)


import datetime
import json
import os

LOG_FILE = "pain_log.json"

def update_agent_pain(pain_level: float):
    timestamp = datetime.datetime.now().isoformat()

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

    print(f"Logged pain level {pain_level} at {timestamp}")
