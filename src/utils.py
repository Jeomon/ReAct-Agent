import re
import ast
def extract_steps(input_string):
    # Regex patterns to capture the first occurrence of Thought, Action, and Action Input
    thought_pattern = r"Thought: ([^\n]+)"
    action_pattern = r"Action: ([^\n]+)"
    action_input_pattern = r"Action Input: ({[^}]+})"
    final_answer_pattern = r"Final Answer: ([^\n]+)"
    
    # Find all matches for Thought, Action, Action Input, and Final Answer
    thought_match = re.search(thought_pattern, input_string, re.DOTALL)
    action_match = re.search(action_pattern, input_string, re.DOTALL)
    action_input_match = re.search(action_input_pattern, input_string, re.DOTALL)
    final_answer_match = re.search(final_answer_pattern, input_string, re.DOTALL)

    thought = thought_match.group(1).strip() if thought_match else None
    action_name = action_match.group(1).strip() if action_match else None
    action_input_str = action_input_match.group(1).strip() if action_input_match else None
    final_answer = final_answer_match.group(1).strip() if final_answer_match else None

    # Convert the action input string to a dictionary
    action_input = ast.literal_eval(action_input_str) if action_input_str else None
    
    return thought, action_name, action_input, final_answer