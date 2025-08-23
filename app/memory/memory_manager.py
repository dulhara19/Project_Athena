agent_memory = {
    "user_profile": {
        "name": "Lakshan",
        "age": 23,
        "goals": ["learn AI", "become millionaire"]
    },
    "emotional_traits": {
        "strengths": ["hardworking", "curious"],
        "weaknesses": ["impatient"],
        "attitudes": ["positive"]
    },
    "chat_history": []
}

# update profile dynamically
agent_memory["user_profile"]["age"] = 24  
agent_memory["emotional_traits"]["weaknesses"].append("self-doubt")
agent_memory["chat_history"].append("User asked about LinkedIn post")
