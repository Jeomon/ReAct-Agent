from langgraph.graph import StateGraph,END
from typing import TypedDict,Annotated
from src.agent import BaseAgent
from src.message import BaseMessage,SystemMessage,HumanMessage,AIMessage
from src.agent.react.prompt import react_prompt
from src.utils import extract_steps
from src.inference import BaseInference
from operator import add
from json import loads,dumps
from getpass import getuser
from os import getcwd
from platform import system

class AgentState(TypedDict):
    input:str
    output:str
    messages:Annotated[list[BaseMessage],add]

class ReActAgent(BaseAgent):
    def __init__(self,name:str='',tools=[],llm:BaseInference=None,max_iter:int=5,verbose:bool=False) -> None:
        self.name=name
        self.system_prompt=react_prompt
        self.tools={tool.name:tool for tool in tools}
        self.tool_names=[tool.name for tool in tools]
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
        workflow.add_conditional_edges('reason',self.decision,{'next':'action','end':'final'})
        workflow.add_edge('action','reason')
        workflow.set_finish_point('final')
        return workflow.compile(debug=False)
    
    def reason(self,state):
        messages='\n'.join([message.content for message in state['messages']])
        system_prompt=self.system_prompt.format(name=self.name,tools=self.tools_description,
        tool_names=self.tool_names,input=state['input'],agent_scratchpad=messages,os=system(),
        user=getuser(),cwd=getcwd())
        messages=[SystemMessage(system_prompt)]
        response_message=self.llm.invoke(messages)
        thought,action,action_input,final_answer=extract_steps(response_message.content)
        if self.verbose:
            print(f'Thought: {thought}')
        if action is not None and action_input is not None:
            content=f'Thought: {thought}\nAction: {action}\nAction Input: {action_input}'
        else:
            content=f'Thought: {thought}\nFinal Answer: {final_answer}'
        message=HumanMessage(content)
        return {**state,'messages':[message]}
    
    def decision(self,state):
        last_message=state['messages'][-1]
        _,action,action_input,final_answer=extract_steps(last_message.content)
        if action is not None and action_input is not None:
            return 'next'
        else:
            return 'end'
    
    def action(self,state):
        last_message=state['messages'][-1]
        _,tool_name,tool_input,_=extract_steps(last_message.content)
        if self.verbose:
            print(f'Action: {tool_name}\nAction Input: {tool_input}')
        if tool_name not in self.tool_names:
            observation="Tool not found."
        else:
            try:
                tool=self.tools[tool_name]
                observation=tool(**tool_input)
            except Exception as e:
                observation=f"Error: {e}"
        if self.verbose:
            print(f'Observation: {observation}')
        content=f'Observation: {observation}'
        message=HumanMessage(content)
        return {**state,'messages':[message]}
    
    def final(self,state):
        last_message=state['messages'][-1]
        _,_,_,final_answer=extract_steps(last_message.content)
        if self.verbose:
            print(f'Final Answer: {final_answer}')
        content=f'Final Answer: {final_answer}'
        message=HumanMessage(content)
        return {**state,'messages':[message],'output':final_answer}
    
    def invoke(self,input:str):
        response=self.graph.invoke({'input':input})
        return response['output']
    
    def stream(self,input:str):
        response=self.graph.invoke({'input':input})
        chunks=response['output']
        return (chunk for chunk in chunks)