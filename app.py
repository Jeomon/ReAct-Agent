from agent.react_graph import ReActAgent
from prompt.react_prompt import system_prompt
from inference.groq import ChatGroq
from tools import weather_tool,random_gen_tool,save_tool
from os import environ
from dotenv import load_dotenv

load_dotenv()
api_key=environ.get('GROQ_API_KEY')

llm=ChatGroq('llama3-8b-8192',api_key,temperature=0)
input=input("Enter a query: ")
agent=ReActAgent('Agent',system_prompt,[save_tool,weather_tool],llm)
response=agent.invoke(input)
print(response)