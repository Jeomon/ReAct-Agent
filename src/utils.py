import re
import ast

def extract_llm_response(response):
    # Initialize variables to store extracted information
    thought = None
    action_name = None
    action_input = None
    final_answer = None
    
    # Define regular expressions for different parts of the response
    thought_regex = re.compile(r'Thought:\s*(.*)')
    action_name_regex = re.compile(r'Action Name:\s*(.*)')
    action_input_regex = re.compile(r'Action Input:\s*(\{.*?\})', re.DOTALL)
    final_answer_regex = re.compile(r'Final Answer:\s*(.*)', re.DOTALL)
    
    # Extract thought
    thought_match = thought_regex.search(response)
    if thought_match:
        thought = thought_match.group(1).strip()
    
    # Extract action name
    action_name_match = action_name_regex.search(response)
    if action_name_match:
        action_name = action_name_match.group(1).strip()
    
    # Extract action input
    action_input_match = action_input_regex.search(response)
    if action_input_match:
        action_input_str = action_input_match.group(1).strip()
        try:
            action_input = ast.literal_eval(action_input_str)
        except (ValueError, SyntaxError):
            action_input = action_input_str  # In case of an error, keep it as a string
    
    # Extract final answer
    final_answer_match = final_answer_regex.search(response)
    if final_answer_match:
        final_answer = final_answer_match.group(1).strip()
    
    # Return the extracted information
    return {
        'Thought': thought,
        'Action Name': action_name,
        'Action Input': action_input,
        'Final Answer': final_answer
    }