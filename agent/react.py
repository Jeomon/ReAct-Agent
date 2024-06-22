from agent.base import BaseAgent
from inference.base import BaseInference
from message.base import HumanMessage,AIMessage,SystemMessage
from json import loads

class ReActAgent(BaseAgent):
    def __init__(self,name:str,system_prompt:str,tools:list,llm:BaseInference,max_iter=5,verbose=False) -> None:
        self.name=name
        self.system_prompt=system_prompt
        self.tools={tool.name:tool for tool in tools}
        self.tool_names=self.tools.keys()
        self.tools_description=[f'Tool Name: {tool.name}\n Tool Args: {tool.schema}\n Tool Description: {tool.description}' for tool in tools]
        self.llm=llm
        self.messages=[]
        self.answer=''
        self.max_iter=max_iter
        self.verbose=verbose
    def reason(self):
        system_message=self.system_prompt.format(name=self.name,tools=self.tools_description,tool_names=self.tool_names)
        messages=[SystemMessage(system_message)]+self.messages
        response=self.llm.invoke(messages)
        self.messages.append(response)

    def decision(self):
        last_message=self.messages[-1]
        steps=loads(last_message.content)
        if 'Thought' in steps and self.verbose:
            print('Thought :'+steps['Thought'])
        if 'Final Answer' in steps:
            if self.verbose:
                print('Final Answer :'+steps['Final Answer'])
            self.answer=steps['Final Answer']
            return False
        if 'Action' in steps:
            if self.verbose:
                print('Action :'+str(steps['Action']))
            return True

    def action(self):
        last_message=self.messages[-1]
        steps=loads(last_message.content)
        action=steps['Action']
        if action['Action Name'] not in self.tool_names:
            raise ValueError("The tool is not found.")
        observation=self.tools[action['Action Name']](**action['Action Input'])
        if self.verbose:
            print('Observation :'+observation)
        content='''{{
            "Observation": "{observation}"
        }}'''.format(observation=observation)
        message=HumanMessage(content)
        self.messages.append(message)

    def invoke(self,input):
        self.messages.append(HumanMessage(input))
        iter=0
        while iter<self.max_iter:
            if self.verbose:
                print(f'Iteration #: {iter}')
            self.reason()
            if self.decision():
                self.action()
            else:
                return self.answer
            iter+=1