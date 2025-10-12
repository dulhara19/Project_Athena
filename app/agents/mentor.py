from app.llmconnector import connector
import os
import json
import matplotlib.pyplot as plt

from app.agents.meta import meta_reasoner
from app.agents.wedana import wedana_classifier, update_pain_history, plot_pain_history_fixed
from app.memory.memory_manager import update_agent_pain
from app.emotions.emotion_redis import analyze_user
from app.agents.user_mapper import map_summary_to_fields
from app.agents.combinator import generate_final_response
from app.agents.eval import empathy_from_pain
from app.agents.personality_picker import pick_new_personality_by_user_mbti

# -------------------------------
# File paths and profile utils
# -------------------------------
current_dir = os.path.dirname(__file__)
profile_path = os.path.join(current_dir, "athena_profile.json")

def load_athena_profile(file_path=profile_path):
    with open(file_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    return profile

def get_athena_mbti(profile):
    mbti_info = profile.get("mbti", {})
    return mbti_info.get("mbti", ""), mbti_info

def update_athena_mbti(file_path, new_mbti_dict):
    profile = load_athena_profile(file_path)
    profile["mbti"] = new_mbti_dict
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    return profile["mbti"]

# -------------------------------
# Analyze user input
# -------------------------------
summary = analyze_user("user123", "session1", "i dont want to hear your words anymore. just leave me alone")
user_pain = float(summary.get("pain_level", 0))
user_summary = map_summary_to_fields(summary)
user_input = summary.get("text", "")

print("\n✅ Mapped user summary:")
print(user_summary)

# -------------------------------
# Athena's pain assessment
# -------------------------------
athena_profile = load_athena_profile()
athena_pain_level_res = wedana_classifier(user_input, athena_profile)

# Extract numeric value for empathy metrics only
ath_pain_level = float(athena_pain_level_res.get("final_answer", 0))
print("\n✅ Athena numeric pain level extracted for metrics:", ath_pain_level)

# -------------------------------
# Generate Athena textual response
# -------------------------------
final_res = generate_final_response(
    user_summary=user_summary,
    athena_profile=athena_profile
)

print("\n✅ Athena final textual response:")
print(final_res)  # This is the string wrapped in <final_answer> tags

# -------------------------------
# Update pain history and plot
# -------------------------------
update_pain_history(user_input, ath_pain_level)
plot_pain_history_fixed()

# -------------------------------
# Compute empathy metrics
# -------------------------------
result = empathy_from_pain(ath_pain_level, user_pain)

# Plot empathy metrics
labels = ["empathy", "alignment", "raw_diff", "same_direction", "confidence"]
values = [
    result["empathy"],
    result["alignment"],
    result["raw_diff"] / 2.0,  # normalize raw_diff
    result["same_direction"],
    result["confidence"]
]

plt.figure(figsize=(8,5))
bars = plt.bar(labels, values, color=['#4caf50','#2196f3','#f44336','#ff9800','#9c27b0'])
plt.ylim(0, 1.0)
plt.title("Empathy Metrics from Athena vs User Pain")
plt.ylabel("Score (0..1)")

for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{val:.2f}", ha='center', va='bottom')

plt.show()

# -------------------------------
# Adaptive personality adjustment
# -------------------------------
BIG_MISMATCH_THRESHOLD = 0.5
mismatch = 1 - result["alignment"]

athena_mbti_type, athena_mbti_info = get_athena_mbti(athena_profile)

if mismatch >= BIG_MISMATCH_THRESHOLD:
    user_mbti_type = user_summary.get("personality", {}).get("mbti", "")
    new_personality = pick_new_personality_by_user_mbti(user_mbti_type, athena_mbti_info)

    if new_personality:
        updated_mbti = update_athena_mbti(profile_path, new_personality)
        print("✅ Athena personality updated to complement user MBTI:", updated_mbti)
    else:
        print("⚠️ No suitable personality found to update")
else:
    print("✅ Mismatch not large enough, keeping current personality")


# Run test
# response=classify_question(
#     user_input=user_input,
#     emotion_desc=emotion_desc,
#     personality_desc=personality_desc,
#     memory_desc=memory_desc,
#     human_desc=human_desc,
#     chat_history=chat_history,
#     pain_level =pain_level,
# )
# print("\n✅ answer :")
# print(response)

# meta_res=meta_reasoner(response, emotion_desc, personality_desc, memory_desc, human_desc, chat_history,user_input)
# print("\n✅ Meta Reasonng :") 
# print(meta_res)