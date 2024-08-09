from src.inference import BaseInference
from src.message import AIMessage,HumanMessage,BaseMessage,SystemMessage
from langgraph.graph import END,StateGraph
from src.agent import BaseAgent
from src.tool import tool
from typing import TypedDict,Annotated
import json
import operator

class AgentState(TypedDict):
    input:str
    messages:Annotated[list[BaseMessage],operator.add]
    output:str

class Agent(BaseAgent):
    def __init__(self,name:str='',description:str='',instructions:list[str]=[],tools:list[tool]=[],llm:BaseInference=None,verbose=False):
        with open(r'src\agent\prompt.md','r') as f:
            self.system_prompt=f.read()
        self.tool_names=[tool.name for tool in tools]
        self.tools={tool.name:tool for tool in tools}
        self.tools_description='['+'\n'.join([json.dumps({'Tool Name': tool.name,'Tool Input': tool.schema, 'Tool Description': tool.description},indent=2) for tool in tools])+']'
        self.llm=llm
        self.graph=self.create_graph()
        self.verbose=verbose

    def reason(self,state:AgentState):
        message=self.llm.invoke(state['messages'],json=True)
        response=json.loads(message.content)
        if self.verbose:
            print('Thought: '+response['Thought'])
        return {**state,'messages':[AIMessage(response)]}
    
    def action(self,state:AgentState):
        message=(state['messages'].pop()).content
        action_name=self.tools[message['Action']['Action Name']]
        action_input=message['Action']['Action Input']
        if self.verbose:
            print('Action: '+json.dumps(message['Action'],indent=2))
        observation=action_name(**action_input)
        message['Observation']=f'''{observation}'''
        if self.verbose:
            print('Observation: '+observation)
        return {**state,'messages':[AIMessage(json.dumps(message,indent=2))]}
        
    def final(self,state:AgentState):
        message=(state['messages'][-1]).content
        if self.verbose:
            print('Final Answer: '+message['Final Answer'])
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

    def invoke(self,input:str):
        system_prompt=self.system_prompt.format(tools=self.tools_description,tool_names=self.tool_names)
        state={
            'input':input,
            'messages':[SystemMessage(system_prompt),HumanMessage(input)],
            'output':'',
        }
        response=self.graph.invoke(state)
        # for message in state['messages']:
        #     if isinstance(message,SystemMessage):
        #         print('system')
        #     elif isinstance(message,HumanMessage):
        #         print('human')
        #     else:
        #         print('ai')
        # print(len(state['messages']))
        return response['output']
    
    def stream(self, input: str):
        pass
