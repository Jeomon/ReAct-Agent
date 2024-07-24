from langgraph.graph import StateGraph
from typing import TypedDict,Annotated
from src.agent import BaseAgent
from src.message import BaseMessage,SystemMessage,HumanMessage,AIMessage
from src.agent.react_json.prompt import system_prompt
from src.inference import BaseInference
from operator import add
from json import loads,dumps
from platform import system
from getpass import getuser
from os import getcwd

class AgentState(TypedDict):
    input:str
    output:str
    messages:Annotated[list[BaseMessage],add]

class ReActAgent(BaseAgent):
    def __init__(self,name:str='',tools=[],llm:BaseInference=None,max_iter:int=5,verbose:bool=False) -> None:
        self.name=name
        self.system_prompt=system_prompt
        self.tools={tool.name:tool for tool in tools}
        self.tool_names=self.tools.keys()
        self.tools_description=[f'Tool Name: {tool.name}\n Tool Input: {tool.schema}\n Tool Description: {tool.description}' for tool in tools]
        self.llm=llm
        self.graph=self.create_graph()
        self.iter=0
        self.max_iter=max_iter
        self.verbose=verbose
    
    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('action',self.action)
        workflow.add_node('final',self.final)
        workflow.set_entry_point('reason')
        workflow.add_conditional_edges('reason',self.decision,{False:'action',True:'final'})
        workflow.add_edge('action','reason')
        workflow.set_finish_point('final')
        return workflow.compile()

    def reason(self,state):
        system_prompt=self.system_prompt.format(name=self.name,tools=self.tools_description,
        tool_names=self.tool_names,os=system(),user=getuser(),cwd=getcwd(),input=state['input'])
        messages=[SystemMessage(system_prompt)]+state['messages']
        llm_response=self.llm.invoke(messages,json=True)
        return {**state,'messages':[llm_response]}
    
    def decision(self,state):
        last_message=state['messages'][-1]
        steps=loads(last_message.content)

        if self.verbose:
            print(f"Iteration: {self.iter}")
            print(f'Thought: {steps['Thought']}')

        if self.iter>self.max_iter:
            content="Iteration limit exceeded."
            state['output']=content
            if self.verbose:
                print(f"Final Answer: {content}")
            return True

        if 'Action' in steps:
            if self.verbose:
                content=dumps(steps['Action'],indent=2)
                print(f"Action: {content}")
            self.iter+=1
            return False
        else:
            content=steps['Final Answer']
            if self.verbose:
                print(f"Final Answer: {content}")
            return True
        
    def action(self,state):
        last_message=state['messages'][-1]
        steps=loads(last_message.content)
        action=steps['Action']
        
        if action['Action Name'] not in self.tool_names:
            observation="Tool not found."
        else:
            try:
                action_name=self.tools[action['Action Name']]
                action_input=action['Action Input']
                observation=action_name(**action_input)

            except Exception as e:
                observation=f"Error: {e}"
        content=f'''{{
        "Observation": {observation.strip()}
        }}'''

        if self.verbose:
            print(f"Observation: {observation}")
            
        message=HumanMessage(content)
        return {**state,'messages':[message]}
    
    def final(self,state):
        if self.iter>self.max_iter:
            state['messages'].append(AIMessage(dumps({'Final Answer': 'Iteration limit exceeded.'})))
        last_message=state['messages'][-1]
        output=loads(last_message.content)
        return {**state,'output':output['Final Answer']}
        
    def invoke(self,input:str,):
        response=self.graph.invoke({'input':input})
        return response['output']
    
    def stream(self,input:str):
        response=self.graph.invoke({'input':input})
        chunks=response['output']
        return (chunk for chunk in chunks)