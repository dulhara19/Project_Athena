from app.llmconnector import connector
import os
import json
import json
from app.agents.meta import meta_reasoner
from app.agents.wedana import wedana_classifier
from app.agents.wedana import update_pain_history,plot_pain_history_fixed
from app.memory.memory_manager import update_agent_pain
from app.emotions.emotion_redis import analyze_user
from app.memory.memory_manager import update_agent_pain_log,plot_pain_log
from app.agents.user_mapper import map_summary_to_fields  
from app.agents.combinator import generate_final_response  



summary=analyze_user("user123", "session1","i love you")
print("🟢🟢🟢🟢summary🟢🟢🟢🟢")
print(summary)
user_summary=map_summary_to_fields(summary)
print("🟢🟢🟢🟢user summary🟢🟢🟢🟢")
print(user_summary)
user_input=user_summary.get("latest_text", "")
print("User input:", user_input)
# detecting the pain level using wedana classifier


# Load Athena's profile from JSON file


def load_athena_profile(file_path=None):
    if file_path is None:
        # Get current file directory and join with JSON file
        dir_path = os.path.dirname(__file__)  # directory of this Python file
        file_path = os.path.join(dir_path, "athena_profile.json")
    
    with open(file_path, "r", encoding="utf-8") as f:
        ego_data = json.load(f)
    return ego_data


# Load Athena ego/profile
athena_ego = load_athena_profile()

    # Call the wedana_classifier function
athena_pain_level = wedana_classifier(user_input, athena_ego)
    
ath_pain_level=athena_pain_level["final_answer"]
print(ath_pain_level)

finalres=generate_final_response(
    user_summary=user_summary,
    athena_profile=athena_ego,
    athena_pain_level=ath_pain_level
    )
print(finalres)

# updating the pain level is pain history
update_pain_history(user_input,ath_pain_level)
plot_pain_history_fixed()

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