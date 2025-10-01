import re

def extract_final_answer(text: str) -> str:
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
