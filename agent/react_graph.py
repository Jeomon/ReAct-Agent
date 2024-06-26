from langgraph.graph import StateGraph,END
from typing import TypedDict,Annotated
from agent.base import BaseAgent
from message.base import BaseMessage,SystemMessage,HumanMessage,AIMessage
from operator import add
from json import loads

class AgentState(TypedDict):
    input:str
    messages:Annotated[list[BaseMessage],add]

class ReActAgent(BaseAgent):
    def __init__(self,name='',system_prompt='',tools=[],llm=None,max_iter=5) -> None:
        self.name=name
        self.system_prompt=system_prompt
        self.tools={tool.name:tool for tool in tools}
        self.tool_names=self.tools.keys()
        self.tools_description=[f'Tool Name: {tool.name}\n Tool Input: {tool.schema}\n Tool Description: {tool.description}' for tool in tools]
        self.llm=llm
        self.graph=self.create_graph()
        self.iter=0
        self.max_iter=max_iter
    
    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('action',self.action)
        workflow.set_entry_point('reason')
        workflow.add_conditional_edges('reason',self.decision,{False:'action',True:END})
        workflow.add_edge('action','reason')
        return workflow.compile()

    def reason(self,state):
        question=state['input']
        system_message=self.system_prompt.format(name=self.name,tools=self.tools_description,tool_names=self.tool_names,input=question)
        messages=[SystemMessage(system_message)]+state['messages']
        message=self.llm.invoke(messages)
        return {'messages':[message]}
    
    def decision(self,state):
        last_message=state['messages'][-1]
        steps=loads(last_message.content)
        if 'Final Answer' in steps or self.iter==self.max_iter:
            if self.iter==self.max_iter:
                state['messages'].append(AIMessage("Iteration limit exceeded."))
            return True
        else:
            self.iter+=1
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
        response=self.graph.invoke({'input':input})
        return response

