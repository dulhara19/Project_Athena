
def print_user_memory(user_id: str, n: int = 10):
    entries = get_recent_emotions(user_id, n=n)
    if not entries:
        print(f"No memory for user {user_id}")
        return
    for i, e in enumerate(entries, 1):
        ts = e.get("ts")
        sess = e.get("session_id")
        text = e.get("text")[:200]
        pain = e.get("pain")
        emotions = e.get("emotion", {}).get("emotions")
        print(f"[{i}] {ts} | session={sess} | pain={pain} | text={text}")
        print(f"     emotions: {emotions}")

print_user_memory("user123", n=5)