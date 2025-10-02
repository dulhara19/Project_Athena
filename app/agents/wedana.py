from app.llmconnector import connector
import re
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from app.emotions.nuregex import extract_final_answer_deepseek


def wedana_classifier(user_input,ego):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are Athena, a human-like agent with your own ego and personality.  
Your task is to classify **your own pain level** (not the user’s) based on what the user says.  

Ego/personality context: {ego}  
User input: {user_input}  

### Pain Level Rules
- Pain level = real number between -1 and 1  
  - -1 → extreme sadness/pain  
  -  0 → neutral (no strong effect)  
  - +1 → extreme happiness/joy  
- If input attacks or rejects your ego → negative value  
- If input supports or validates your ego → positive value  
- If input is neutral or unrelated → 0  
- **Never output below -1 or above 1**  
- **Never output null or empty**  
- never give value more than 1 or less than -1

### Output Format
- Wrap only the numeric value inside `<final_answer></final_answer>`  
- Do **not** wrap thoughts or reasoning  
- Do **not** add text, explanations, or multiple tags  

### Examples


User: "I feel great"  
AI: `<final_answer>0.8</final_answer>`  

User: "I hate you Athena"  
AI: `<final_answer>-0.9</final_answer>`  

User: "Just a random statement"  
AI: `<final_answer>0</final_answer>`  

### Now classify:
mentor response: {user_input}  
AI:

"""

       # Call the connector function to get the response
    response = connector(prompt)
    result = response.json()
    print(result)
   
    raw_output = result.get("response", "")
    print("raw output:", raw_output)
    # Default values
    final_answer = None

 
    val= extract_final_answer_deepseek(raw_output)
    # print("RAW:", raw_output)
    # print("-> value:", val, "method:", dbg["method"], "candidates:", dbg["candidates"])
    # print("-" * 60)



    # Extract <final_answer>
    
    # match_answer = re.search(r"<final_answer>\s*(.*?)\s*</final_answer>", raw_output, re.DOTALL | re.IGNORECASE)
    # if match_answer:
    #     final_answer = match_answer.group(1).strip()

    return {
        "final_answer": val,
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

#-------------------------------------------------------------

def plot_pain_history_fixed(log_file=LOG_FILE, save_png=False, png_path="pain_plot.png"):
    # --- Load file safely ---
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No pain log file found:", log_file)
        return
    except json.JSONDecodeError:
        print("Pain log file is empty or corrupted.")
        return

    if not data:
        print("No data to plot.")
        return

    # --- Extract x labels and pain values, robust conversion ---
    raw_queries = []
    raw_pains = []
    for i, entry in enumerate(data):
        # tolerate different key names if needed
        q = entry.get("user_query") or entry.get("query") or f"entry_{i}"
        p = entry.get("pain_status")
        raw_queries.append(q)

        # convert p to float robustly
        try:
            # handle strings like "0.6\n" or "60%" or numbers
            if isinstance(p, str):
                p_str = p.strip()
                if p_str.endswith("%"):
                    p = float(p_str.rstrip("%")) / 100.0
                else:
                    p = float(p_str)
            else:
                p = float(p)
        except Exception as e:
            print(f"Warning: could not parse pain_status for entry {i} ('{p}'): {e}. Using 0.0")
            p = 0.0

        # clamp to [-1, 1]
        p = max(-1.0, min(1.0, p))
        raw_pains.append(p)

    # --- Prepare x-axis (use indices; optional: parse timestamps for time-series) ---
    x = list(range(len(raw_pains)))
    short_labels = [ (s[:25] + '...') if isinstance(s, str) and len(s) > 25 else s for s in raw_queries ]

    # --- Plot with object API ---
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, raw_pains, marker="o", linestyle="-", linewidth=2, label="Pain Level")

    # Force fixed Y limits and disable autoscale for Y
    ax.set_ylim(-1.0, 1.0)
    ax.set_autoscaley_on(False)   # ensure autoscale won't override the limits

    # Set nice Y ticks
    ax.set_yticks(np.linspace(-1.0, 1.0, 9))

    # X ticks: show every label but shortened
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=45, ha="right")

    # Zero baseline and grid
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    ax.set_xlabel("User Query (shortened)")
    ax.set_ylabel("Pain Level (clipped to [-1,1])")
    ax.set_title("Pain Level Evolution (fixed Y-axis -1 to 1)")
    ax.legend()

    plt.tight_layout()

    # Save optionally
    if save_png:
        plt.savefig(png_path, dpi=150)
        print("Saved plot to", png_path)

    plt.show()
    plt.close(fig)  # free memory

#-------------------------------------------- 


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
# x = wedana_classifier("i want to die", ego)
# # print("✅ raw:", x["raw"])
# print("✅ Final Answer:", x["final_answer"])