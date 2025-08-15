from datetime import datetime

# Main storage
users_data = {}

def update_user_data(
    user_id,
    query=None,
    profile_updates=None,
    emotional_updates=None
):
    """
    Updates user profile, emotional characteristics, and chat history.

    Args:
        user_id (str): Unique ID for the user
        query (str): User query text (optional)
        profile_updates (dict): New/updated profile fields
        emotional_updates (dict): New/updated emotional characteristics
    """

    # If user doesn't exist, initialize
    if user_id not in users_data:
        users_data[user_id] = {
            "profile": {},
            "emotional": {},
            "chat_history": []
        }

    # Update profile
    if profile_updates:
        users_data[user_id]["profile"].update(profile_updates)

    # Update emotional data
    if emotional_updates:
        users_data[user_id]["emotional"].update(emotional_updates)

    # Add chat history
    if query:
        users_data[user_id]["chat_history"].append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })

    return users_data[user_id]


# ---------------- Example Usage ----------------

# First update
update_user_data(
    user_id="user123",
    profile_updates={"name": "Lakshan", "email": "lakshan@example.com"},
    emotional_updates={"strength": "resilient", "weakness": "overthinking"},
    query="How do I improve my time management?"
)

# Update emotions later
update_user_data(
    user_id="user123",
    emotional_updates={"attitude": "optimistic", "weakness": "impatience"},
    query="I feel stressed lately."
)

# View stored data
from pprint import pprint
pprint(users_data)
