import random

def calculate_emotions(agent_state, events):
    """
    Updates the agent's emotional state based on incoming events.

    agent_state: dict holding current emotion levels
    events: list of dicts, each with 'type' and 'intensity' (positive/negative value)

    Example:
    agent_state = {"happiness": 0.5, "anger": 0.2, "fear": 0.1}
    events = [{"type": "compliment", "intensity": 0.3}, {"type": "insult", "intensity": -0.5}]
    """

    # Define how each event type maps to emotions
    emotion_map = {
        "compliment": {"happiness": 0.4, "anger": -0.2, "fear": -0.1},
        "insult": {"happiness": -0.4, "anger": 0.5, "fear": 0.2},
        "threat": {"happiness": -0.3, "anger": 0.3, "fear": 0.6},
        "joke": {"happiness": 0.5, "anger": -0.1, "fear": -0.2}
    }

    # Emotion decay factor (fades towards 0.0)
    decay_rate = 0.05

    # First apply decay so emotions slowly go back to neutral
    for emotion in agent_state:
        if agent_state[emotion] > 0:
            agent_state[emotion] = max(0.0, agent_state[emotion] - decay_rate)
        elif agent_state[emotion] < 0:
            agent_state[emotion] = min(0.0, agent_state[emotion] + decay_rate)

    # Apply each event's influence
    for event in events:
        if event["type"] in emotion_map:
            for emotion, weight in emotion_map[event["type"]].items():
                change = weight * event["intensity"]
                agent_state[emotion] += change

                # Clamp emotion values between -1 and 1
                agent_state[emotion] = max(-1.0, min(1.0, agent_state[emotion]))

    return agent_state





agent_state = {"happiness": 0.5, "anger": 0.2, "fear": 0.1}

events = [
    {"type": "compliment", "intensity": 0.3},
    {"type": "insult", "intensity": 0.6}
]

new_state = calculate_emotions(agent_state, events)
print(new_state)
