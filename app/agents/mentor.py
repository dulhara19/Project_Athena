from llmconnector import connector

def classify_question(user_input):
    # Prepare the prompt with the user input
    prompt = f"""
    You are a classifier that determines whether a user question for a university chatbot is about "structured" data, "unstructured" information, or a "hybrid" of both.

    Your task is to output ONLY one of these three categories wrapped inside <final_answer> tags:
    - structured → questions about timetables, bus schedules, or cafe menus (data stored in structured databases)
    - unstructured → questions about university policies, procedures, modules, subjects, degree or general information (not included: timetables, cafe menus, bus schedules)
    - hybrid → questions containing both structured and unstructured information requests in the same input.
    - If user asks multiple questions just classify as hybrid

    Examples:
    - "What time is the math lecture on Monday?" → <final_answer>structured</final_answer>
    - "How do I apply for medical leave if I missed an exam?" → <final_answer>unstructured</final_answer>
    - "When is the next chemistry exam and how do I request a medical leave?" → <final_answer>hybrid</final_answer>

    Now classify this input:
    "{user_input}"
    """

    # Call the connector function to get the response
    response = connector(prompt)

    # Parse the response to extract the final answer
    if response.status_code == 200:
        return response.json().get('text', 'No classification found')
    else:
        return 'Error in classification'
