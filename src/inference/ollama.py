from src.inference import BaseInference
from src.message import AIMessage,BaseMessage
from requests import post
from json import loads
from typing import Literal

class ChatOllama(BaseInference):
    def invoke(self,messages: list[BaseMessage],stream=False,json=False)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":stream
        }
        try:
            response=post(url=url,json=payload,headers=headers)
            json_obj=response.json()
            print(json_obj)
            return AIMessage(json_obj['message']['content'])
        except Exception as err:
            print(err)
    
    def stream(self,messages: list[BaseMessage],json=False):
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            response=post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['message']['content'] for chunk in chunks)
        except Exception as err:
            print(err)

class Ollama(BaseInference):
    def invoke(self, query:str,json=False)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":False
        }
        try:
            response=post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_obj=response.json()
            return AIMessage(json_obj['response'])
        except Exception as err:
            print(err)

    def stream(self,query:str,json=False):
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            response=post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['response'] for chunk in chunks)
        except Exception as err:
            print(err)
