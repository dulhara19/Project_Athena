from app.llmconnector import connector
import re

def meta_reasoner(input):
    # Prepare the prompt with the user input and other details
    prompt = f"""
You are an AI assistant that help student to make their studies

now user says : {input}
AI:
"""    

    # Call the connector function to get the response
    # Send request to LLM
    response = connector(prompt)
    print(response)
    # Parse and extract classification
    result = response.json()
    print(result)
    # raw_output = result.get("response", "")

    # debugging---
    # Print raw output for debugging
    # print("\n✅ Raw LLM Output:\n", raw_output)

    # Extract <final_answer>
    # match = re.search(r"<final_answer>\s*(.*?)\s*</final_answer>", raw_output, re.DOTALL | re.IGNORECASE)

    # if match:
    #     final_answer = match.group(1).strip()
        
    #     # print(final_answer)
    #     return final_answer

meta_reasoner("im bad at maths. tell me how to improve my math skills")