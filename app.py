from src.agent.react import ReActAgent
from src.inference.groq import ChatGroq
from tools import terminal_tool,save_tool,weather_tool,search_tool
from os import environ
from dotenv import load_dotenv

load_dotenv()
api_key=environ.get('GROQ_API_KEY')

llm=ChatGroq('llama3-8b-8192',api_key,temperature=0)
input=input("Enter a query: ")
agent=ReActAgent('Agent',[save_tool,terminal_tool],max_iter=10,llm=llm,verbose=True)
response=agent.stream(input)
for chunk in response:
    print(chunk,flush=False,end='')