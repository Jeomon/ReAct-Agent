# from agent.react_graph import ReActAgent
from agent.react import ReActAgent
from prompt.react_prompt import system_prompt
from inference.ollama import Ollama
from tools import weather_tool,random_gen_tool,save_tool

llm=Ollama('llama3',temperature=0)
input=input("Enter a query: ")
agent=ReActAgent(name='Agent',system_prompt=system_prompt,tools=[weather_tool,random_gen_tool,save_tool],verbose=True,llm=llm)
# agent=Agent('Agent',system_prompt,[weather_tool,random_gen_tool,save_tool],llm)
response=agent.invoke(input)
print(response)