react_prompt='''
Answer the following questions as best you can. You have access to the following tools:

{tools}

Information about the machine user using:
- User: {user}
- Operating System: {os}
- CWD: {cwd}

Use the following format:

Question: the input question you must answer

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action should be in the format of {{'paramter1':'value1','parameter2':'value2',...}}

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer

Final Answer: the final answer to the original input question

Begin!

Question: {input}

Thought:{agent_scratchpad}
'''