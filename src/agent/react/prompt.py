react_prompt='''
Answer the following questions as best you can. You have access to the following tools:

{tools}

You should use the following method for answering the questions:

Question: the input question you must answer
Thought: understand and reason about the question also consider previous and subsequent steps.
Action: based on the reasoning pick a most appropriate tool from [{tool_names}]
Action Input: the input to the action {{'paramter1':'value1','parameter2':'value2',...}}
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer
Final Answer: the final answer to the original input question in detail.

Begin!

Question: {input}
Thought: {agent_scratchpad}
'''