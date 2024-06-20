from abc import ABC,abstractmethod

class BaseInference(ABC):
    def __init__(self,model:str,api_key:str='',base_url:str='',temperature:float=0.5):
        self.model=model
        self.api_key=api_key
        self.base_url=base_url
        self.temperature=temperature
        self.headers={'Content-Type': 'application/json'}
    @abstractmethod
    def invoke(self,messages:list[dict]):
        pass