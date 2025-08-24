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



def update_agent_memory(memory, section, key=None, value=None, append=False):
    """
    Dynamically update agent memory.
    - section: which part ("user_profile", "emotional_traits", "chat_history")
    - key: field to update inside section (optional)
    - value: new value
    - append: if True, appends instead of replacing
    """

    if section not in memory:
        memory[section] = {} if key else []

    if key:
        if append and isinstance(memory[section].get(key), list):
            memory[section][key].append(value)
        else:
            memory[section][key] = value
    else:
        # no key → directly append or set whole section
        if append and isinstance(memory[section], list):
            memory[section].append(value)
        else:
            memory[section] = value

    return memory

agent_memory = {
    "user_profile": {"name": "Lakshan"},
    "emotional_traits": {"strengths": [], "weaknesses": []},
    "chat_history": []
}

# Update user age
update_agent_memory(agent_memory, "user_profile", "age", 24)

# Add a strength
update_agent_memory(agent_memory, "emotional_traits", "strengths", "resilient", append=True)

# Add chat history
update_agent_memory(agent_memory, "chat_history", value="Asked about agent design", append=True)

print(agent_memory)
