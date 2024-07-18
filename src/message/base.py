from abc import ABC

class BaseMessage(ABC):
    def to_dict(self)->dict[str,str]:
        return {
            'role':self.role,
            'content':self.content
        }
    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{class_name}({attributes})"

class HumanMessage(BaseMessage):
    def __init__(self,content:str=''):
        self.role='user'
        self.content=content

class AIMessage(BaseMessage):
    def __init__(self,content:str=''):
        self.role='assistant'
        self.content=content
        
class SystemMessage(BaseMessage):
    def __init__(self,content:str=''):
        self.role='system'
        self.content=content
