from agent.react_graph import ReActAgent
# from agent.react import ReActAgent
from prompt.react_prompt import system_prompt
# from inference.ollama import ChatOllama
from inference.groq import ChatGroq
from tools import weather_tool,random_gen_tool,save_tool
from os import environ
from dotenv import load_dotenv

load_dotenv()
api_key=environ.get('GROQ_API_KEY')


# llm=ChatOllama('llama3',temperature=0)
llm=ChatGroq('llama3-8b-8192',api_key,temperature=0)
input=input("Enter a query: ")
# agent=ReActAgent(name='Agent',system_prompt=system_prompt,tools=[weather_tool,random_gen_tool,save_tool],verbose=True,llm=llm)
agent=ReActAgent('Agent',system_prompt,[weather_tool,random_gen_tool,save_tool],llm)
response=agent.invoke(input)
print(response)