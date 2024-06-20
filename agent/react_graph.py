from langgraph.graph import StateGraph,END
from typing import TypedDict,Annotated
from agent.base import BaseAgent
from message.base import BaseMessage,SystemMessage,HumanMessage
from operator import add
from json import loads

class AgentState(TypedDict):
    messages:Annotated[list[BaseMessage],add]

class ReActAgent(BaseAgent):
    def __init__(self,name='',system_prompt='',tools=[],llm=None) -> None:
        self.name=name
        self.system_prompt=system_prompt
        self.tools={tool.name:tool for tool in tools}
        self.tool_names=self.tools.keys()
        self.tools_description=[f'Tool Name: {tool.name}\n Tool Args: {tool.schema}\n Tool Description: {tool.description}' for tool in tools]
        self.llm=llm
        self.graph=self.create_graph()
    
    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('action',self.action)
        workflow.set_entry_point('reason')
        workflow.add_conditional_edges('reason',self.decision,{False:'action',True:END})
        workflow.add_edge('action','reason')
        return workflow.compile()

    def reason(self,state):
        system_message=self.system_prompt.format(name=self.name,tools=self.tools_description,tool_names=self.tool_names)
        messages=[SystemMessage(system_message)]+state['messages']
        message=self.llm.invoke(messages)
        return {'messages':[message]}
    
    def decision(self,state):
        last_message=state['messages'][-1]
        steps=loads(last_message.content)
        if 'Final Answer' in steps:
            return True
        else:
            return False
        
    def action(self,state):
        last_message=state['messages'][-1]
        steps=loads(last_message.content)
        action=steps['Action']
        if action['Action Name'] not in self.tool_names:
            raise ValueError("The tool is not found.")
        observation=self.tools[action['Action Name']](**action['Action Input'])
        content='''{{
            "Observation": "{observation}"
        }}'''.format(observation=observation)
        message=HumanMessage(content)
        return {'messages':[message]}
        
    def invoke(self,input:str):
        response=self.graph.invoke({'messages':[HumanMessage(input)]})
        return response

