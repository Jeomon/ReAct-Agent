from src.inference import BaseInference
from src.message import AIMessage,HumanMessage,BaseMessage,SystemMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import Image,display
from langgraph.graph import StateGraph
from src.agent import BaseAgent
from typing import TypedDict,Annotated
from termcolor import colored
import json
import operator

class AgentState(TypedDict):
    input:str
    messages:Annotated[list[BaseMessage],operator.add]
    output:str

class Agent(BaseAgent):
    def __init__(self,name:str='',description:str='',instructions:list[str]=[],tools:list=[],llm:BaseInference=None,verbose=False):
        self.name=name
        self.description=description
        self.instructions='\n'.join([f'{i+1}. {instruction}' for i,instruction in enumerate(instructions)])
        self.tool_names=[tool.name for tool in tools]
        self.tools_description='['+'\n'.join([json.dumps({'Tool Name': tool.name,'Tool Input': tool.schema, 'Tool Description': tool.description},indent=2) for tool in tools])+']'
        self.tools={tool.name:tool for tool in tools}
        self.llm=llm
        self.verbose=verbose
        with open(r'src\agent\react_json_prompt.md','r') as f:
            self.system_prompt=f.read()
        self.graph=self.create_graph()

    def reason(self,state:AgentState):
        message=self.llm.invoke(state['messages'],json=True)
        response=json.loads(message.content)
        if self.verbose:
            print(colored(f'Thought: {response['Thought']}',color='green',attrs=['bold']))
        return {**state,'messages':[AIMessage(response)]}

    def action(self,state:AgentState):
        message=(state['messages'].pop()).content
        action_name=self.tools[message['Action']['Action Name']]
        action_input=message['Action']['Action Input']
        if self.verbose:
            print(colored(f'Action: {json.dumps(message['Action'],indent=2)}',color='cyan',attrs=['bold']))
        observation=action_name(**action_input)
        message['Observation']=f'''{observation}'''
        if self.verbose:
            print(colored(f'Observation: {observation}',color='magenta',attrs=['bold']))
        return {**state,'messages':[AIMessage(json.dumps(message,indent=2))]}
        
    def final(self,state:AgentState):
        message=(state['messages'][-1]).content
        if self.verbose:
            print(colored(f'Final Answer: {message['Final Answer']}',color='blue',attrs=['bold']))
        return {**state,'output':message['Final Answer']}

    def controller(self,state:AgentState):
        message=(state['messages'][-1]).content
        if "Action" in message:
            return 'action'
        else:
            return 'final'

    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('action',self.action)
        workflow.add_node('final',self.final)

        workflow.set_entry_point('reason')
        workflow.add_conditional_edges('reason',self.controller)
        workflow.add_edge('action','reason')
        workflow.set_finish_point('final')

        return workflow.compile(debug=False)
    
    def plot_mermaid(self):
        plot=self.graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        return display(Image(plot))

    def invoke(self,input:str):
        parameters={
            'name':self.name,
            'description':self.description,
            'instructions':self.instructions,
            'tools':self.tools_description,
            'tool_names':self.tool_names
        }
        system_prompt=self.system_prompt.format(**parameters)
        state={
            'input':input,
            'messages':[SystemMessage(system_prompt),HumanMessage(input)],
            'output':'',
        }
        response=self.graph.invoke(state)
        return response['output']
    
    def stream(self, input: str):
        pass
