from src.agent.react import Agent
from src.inference.groq import ChatGroq
from tools import terminal_tool,save_tool,weather_tool,search_tool
from os import environ
from dotenv import load_dotenv

load_dotenv()
api_key=environ.get('GROQ_API_KEY')
llm=ChatGroq('llama-3.1-70b-versatile',api_key,temperature=0)
input=input("Enter a query: ")
agent=Agent('AI Agent','You are a helpful AI Assistant',[],tools=[terminal_tool,weather_tool,search_tool,save_tool],llm=llm,verbose=True)
response=agent.invoke(input)
print(response)