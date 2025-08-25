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



import json
import matplotlib.pyplot as plt


LOG_FILE = "pain_log.json"

def plot_pain_log():
    # Load the JSON log
    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    # Extract timestamps and pain levels
    timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in data]
    pain_levels = [entry["pain_level"] for entry in data]

    # Plot graph
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, pain_levels, marker="o", linestyle="-", linewidth=2)

    # Labels and title
    plt.title("Pain Level Over Time")
    plt.xlabel("Time")
    plt.ylabel("Pain Level (0-1)")
    plt.xticks(rotation=30)
    plt.grid(True)
    plt.tight_layout()

    # Show graph
    plt.show()

if __name__ == "__main__":
    plot_pain_log()



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

import json
import os

LOG_FILE = "pain_log.json"

def update_agent_pain_log(pain_level: float):
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
