import re

def extract_final_answer(text: str) -> str:
    """
    Extracts the content inside <final_answer>, <final>, or <answer> tags from LLM output.
    Returns the extracted string. If no tags found, returns the original text stripped.

    Handles:
    - malformed closing tags
    - extra spaces
    - mixed case tags
    """
    # define possible tag names
    tag_names = ["final_answer", "final", "answer"]
    
    # build regex pattern to capture content inside tags
    pattern = r"<\s*({tags})\s*>[\s\S]*?<\s*/\s*\1\s*>".format(tags="|".join(tag_names))
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        # extract content inside the first match
        inner_text = re.sub(r"<.*?>", "", match.group(0))  # remove any remaining inner tags
        return inner_text.strip()
    
    # fallback: no proper tags found, try to remove stray opening/closing tag text
    for t in tag_names:
        text = re.sub(rf"<\s*{t}\s*>", "", text, flags=re.IGNORECASE)
        text = re.sub(rf"<\s*/\s*{t}\s*>", "", text, flags=re.IGNORECASE)
    
    return text.strip()
