from abc import ABC,abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def invoke(self):
        pass
