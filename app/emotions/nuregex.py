import re

def extract_final_answer_deepseek(text: str) -> str:
    """
    Extracts the final answer from LLM outputs.
    Handles:
    - tags: <final_answer>, <final>, <answer> (case insensitive)
    - malformed tags
    - prefix style: "Final answer:", "Final response:", "Answer:"
    - returns a clean string
    """
    # 1️⃣ Try to extract from tags first
    tag_names = ["final_answer", "final", "answer"]
    pattern_tags = r"<\s*({tags})\s*>[\s\S]*?<\s*/\s*\1\s*>".format(tags="|".join(tag_names))
    
    match = re.search(pattern_tags, text, re.IGNORECASE)
    if match:
        inner_text = re.sub(r"<.*?>", "", match.group(0))  # remove any remaining tags inside
        return inner_text.strip()
    
    # 2️⃣ Try to extract from prefix style
    prefix_names = ["Final answer", "Final response", "Answer"]
    for prefix in prefix_names:
        pattern_prefix = rf"{prefix}\s*[:\-]\s*\"?(.*?)\"?$"
        match_prefix = re.search(pattern_prefix, text, re.IGNORECASE)
        if match_prefix:
            return match_prefix.group(1).strip()
    
    # 3️⃣ Fallback: remove stray tag text and return stripped text
    for t in tag_names:
        text = re.sub(rf"<\s*{t}\s*>", "", text, flags=re.IGNORECASE)
        text = re.sub(rf"<\s*/\s*{t}\s*>", "", text, flags=re.IGNORECASE)
    
    return text.strip()


import re

# def extract_final_answer_gpt(text: str) -> float:
#     """
#     Extracts a numeric final answer from LLM outputs.
#     - Returns a float between -1 and 1.
#     - Handles tags: <final_answer>, <final>, <answer> (case-insensitive)
#     - Handles prefix styles: "Final answer:", "Answer:", "Final response:"
#     - Ignores any surrounding text, comments, or emojis
#     - Falls back to 0 if no valid number is found
#     """
#     if not text:
#         return 0.0

#     text = text.strip()

#     # 1️⃣ Try to extract from tags
#     tag_names = ["final_answer", "final", "answer"]
#     tag_pattern = r"<\s*({tags})\s*>[\s\S]*?<\s*/\s*\1\s*>".format(tags="|".join(tag_names))
#     match = re.search(tag_pattern, text, re.IGNORECASE)
#     if match:
#         inner = re.sub(r"<.*?>", "", match.group(0))  # remove any nested tags
#         text = inner.strip()

#     # 2️⃣ Try to extract from prefix style
#     prefix_names = ["Final answer", "Final response", "Answer"]
#     for prefix in prefix_names:
#         pattern_prefix = rf"{prefix}\s*[:\-]\s*\"?(.*?)\"?$"
#         match_prefix = re.search(pattern_prefix, text, re.IGNORECASE)
#         if match_prefix:
#             text = match_prefix.group(1).strip()
#             break  # stop at first match

#     # 3️⃣ Extract first valid number in the text
#     num_match = re.search(r"([-+]?\d*\.?\d+)", text)
#     if num_match:
#         try:
#             val = float(num_match.group(1))
#             # Clamp to [-1, 1]
#             val = max(-1.0, min(1.0, val))
#             return val
#         except:
#             return 0.0

#     # 4️⃣ Fallback: return 0 if no number found
#     return 0.0




# -------------------------
# quick examples / tests
# if __name__ == "__main__":
#     examples = [
#         "<0final_answer>-1</final>, <final_answer>0</final>0</final>, final_answer>0</final>0</final> <final_answer>0</final_answer>0</final>",
#         "Final answer should be0. Need wrap in tags. </think>\n<final_answer>0</final>0</final>",
#         "<final_answer>0.6</final_answer>",
#         "nothing here",
#         "some text final_answer: -0.3 and more text"
#     ]
#     for ex in examples:
#         val, dbg = extract_pain_level(ex)
#         print("RAW:", ex)
#         print("-> value:", val, "method:", dbg["method"], "candidates:", dbg["candidates"])
#         print("-" * 60)
