from agent.react import ReActAgent
from inference.groq import ChatGroq
from tools import terminal_tool,save_tool,weather_tool
from os import environ
from dotenv import load_dotenv

load_dotenv()
api_key=environ.get('GROQ_API_KEY')

llm=ChatGroq('llama3-8b-8192',api_key,temperature=0)
input=input("Enter a query: ")
agent=ReActAgent('Agent',[terminal_tool,save_tool,weather_tool],llm,verbose=False)
response=agent.stream(input)
for message in response:
    print(message)